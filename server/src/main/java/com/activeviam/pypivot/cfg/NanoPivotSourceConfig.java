/*
 * (C) ActiveViam 2018
 * ALL RIGHTS RESERVED. This material is the CONFIDENTIAL and PROPRIETARY
 * property of Quartet Financial Systems Limited. Any unauthorized use,
 * reproduction or transfer of this material is strictly prohibited
 */
package com.activeviam.pypivot.cfg;

import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.STORE_RUSSIA2018;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.DependsOn;
import org.springframework.core.env.Environment;

import com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig;
import com.qfs.gui.impl.JungSchemaPrinter;
import com.qfs.msg.IMessageChannel;
import com.qfs.msg.csv.ICSVSourceConfiguration;
import com.qfs.msg.csv.ICSVTopic;
import com.qfs.msg.csv.IFileInfo;
import com.qfs.msg.csv.ILineReader;
import com.qfs.msg.csv.filesystem.impl.FileSystemCSVTopicFactory;
import com.qfs.msg.csv.impl.CSVSource;
import com.qfs.msg.csv.impl.FileSystemCSVMonitoring;
import com.qfs.source.impl.CSVMessageChannelFactory;
import com.qfs.store.IDatastore;
import com.qfs.store.impl.SchemaPrinter;
import com.qfs.store.transaction.ITransactionManager;
import com.qfs.util.timing.impl.StopWatch;
import com.quartetfs.fwk.QuartetRuntimeException;
import com.quartetfs.fwk.monitoring.jmx.impl.JMXEnabler;

/**
 * Spring configuration for data sources
 *
 * @author ActiveViam
 *
 */
public class NanoPivotSourceConfig {

	private static final Logger LOGGER = Logger.getLogger(NanoPivotSourceConfig.class.getSimpleName());

	/**  Topic for "World Cup 2018" data feed*/
	public static final String WC2018_TOPIC = "WC2018Topic";

	@Autowired
	protected Environment env;

	@Autowired
	protected IDatastore datastore;

	/*
	 * **************************** CSV Source **********************************
	 * This is an example of CSV source configuration, which you could modify to
	 * fit your needs
	 * **************************************************************************
	 */

	/**
	 * Topic factory bean. Allows to create CSV topics and watch changes to directories. Autocloseable.
	 * @return the topic factory
	 */
	@Bean
	public FileSystemCSVTopicFactory csvTopicFactory() {
		return new FileSystemCSVTopicFactory(false);
	}

	/**
	 * Creates the {@link CSVSource} responsible for loading the initial data in
	 * the datastore from csv files.
	 *
	 * @return the {@link CSVSource}
	 * @throws IOException if the source file can't be open or the header is missing
	 */
	@Bean
	public CSVSource<Path> csvSource() throws IOException {
		final FileSystemCSVTopicFactory csvTopicFactory = csvTopicFactory();
		final CSVSource<Path> csvSource = new CSVSource<>(() -> {
			try {
				csvTopicFactory.getWatcherService().close();
			} catch (final IOException ex) {
				LOGGER.log(Level.WARNING, "Problem occurred while closing the watcher service", ex);
			}
		});

		final char separator = env.getProperty("separator", ",").charAt(0);
		final String regexSeparatorForString = "\\" + separator;
		final String fileName = env.getProperty("source.file");
		// final List<String> columns = extractCVSFileColumns(
		// 		getClass().getClassLoader().getResource(fileName).getFile(),
		// 		regexSeparatorForString);
		final List<String> columns = Arrays.asList("gameId", "Team1Name", "Team2Name", "GameDate", "GameTime", "Team1Score", "Team2Score");

		final ICSVTopic<Path> wc2018Topic = csvTopicFactory.createTopic(
				WC2018_TOPIC,
				fileName,
				csvSource.createParserConfiguration(columns));
		wc2018Topic.getParserConfiguration().setCharset(Charset.forName("UTF-8"));
		wc2018Topic.getParserConfiguration().setSeparator(separator);
		wc2018Topic.getParserConfiguration().setAcceptOverflowingLines(true);
		wc2018Topic.getParserConfiguration().setNumberSkippedLines(1); // skipping the first line as it's the header with column names already extracted by extractCVSFileColumns(...) method

		csvSource.addTopic(wc2018Topic);

		final Properties sourceProperties = new Properties();
		sourceProperties.put(ICSVSourceConfiguration.PARSER_THREAD_PROPERTY, env.getProperty("parserThreads"));
		csvSource.configure(sourceProperties);

		return csvSource;

	}

	public List<String> extractCVSFileColumns(String fileName, String separator) throws IOException {

		LOGGER.info("detecting CSV columns for file: " + fileName);

		try (BufferedReader reader = new BufferedReader(new FileReader(fileName))) {
			String header = reader.readLine();
			reader.close();
			if (header.isEmpty()) {
				throw new QuartetRuntimeException("Cannot process empty file: " + fileName);
			}

			final List<String> columns = Arrays.asList(header.split(separator));
			LOGGER.info("Column names: " + columns);

			return columns;

		}
	}

	@Bean
	public CSVMessageChannelFactory<Path> csvChannelFactory() throws IOException {
		final CSVMessageChannelFactory<Path> csvChannelFactory = new CSVMessageChannelFactory<>(csvSource(), datastore);

		// Suggestion: Calculated columns could be defined and added here

		return csvChannelFactory;
	}

	// Enabling JMX on CSV source
	@Bean
	public JMXEnabler jmxCsvSourceEnabler() throws IOException {
		return new JMXEnabler(new FileSystemCSVMonitoring(csvSource()));
	}


	/*
	 * ************************* Other Sources **********************************
	 * Suggestion: You might use instead or add other sources types like
	 * 					  jdbc, POJO, ...
	 * **************************************************************************
	 */


	/*
	 * **************************** Initial load *********************************
	 */
	@Bean
	@DependsOn(value = "startManager")
	public Void initialLoad() throws Exception {

		// csv
		final Collection<IMessageChannel<IFileInfo<Path>, ILineReader>> csvChannels = new ArrayList<>();
		csvChannels.add(csvChannelFactory().createChannel(WC2018_TOPIC, STORE_RUSSIA2018));
		// Suggestion: if any, add other csv source(s)

		// Suggestion: If any, create Message channels for other source type(s) as well


		// Start Transaction
		final long before = System.nanoTime();
		final ITransactionManager transactionManager = datastore.getTransactionManager();
		transactionManager.startTransaction();

		// fetch the source(s) and perform bulk transaction
		csvSource().fetch(csvChannels);

		// Commit Transaction
		transactionManager.commitTransaction();
		final long elapsed = System.nanoTime() - before;

		LOGGER.info("Initial load completed in " + elapsed / 1000000L + "ms");

		printStoreSizes();

		return null;

	}

	private void printStoreSizes() {
		// add some logging
		if (Boolean.parseBoolean(env.getProperty("storeStructure.display", "true"))) {
			// display the graph
			new JungSchemaPrinter(false).print("NanoPivot datastore", datastore);

			// example of printing a store content
			SchemaPrinter.printStore(datastore, DatastoreDescriptionConfig.STORE_RUSSIA2018);
		}

		// Print stop watch profiling
		StopWatch.get().printTimings();
		StopWatch.get().printTimingLegend();

		// print sizes
		SchemaPrinter.printStoresSizes(datastore.getHead().getSchema());
	}

}
