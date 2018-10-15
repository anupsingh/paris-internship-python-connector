/*
 * (C) ActiveViam 2018
 * ALL RIGHTS RESERVED. This material is the CONFIDENTIAL and PROPRIETARY
 * property of Quartet Financial Systems Limited. Any unauthorized use,
 * reproduction or transfer of this material is strictly prohibited
 */
package com.activeviam.pypivot.cfg.datastore;

import static com.qfs.literal.ILiteralType.INT;
import static com.qfs.literal.ILiteralType.STRING;

import java.util.Collection;
import java.util.LinkedList;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.qfs.desc.IDatastoreSchemaDescription;
import com.qfs.desc.IReferenceDescription;
import com.qfs.desc.IStoreDescription;
import com.qfs.desc.impl.DatastoreSchemaDescription;
import com.qfs.desc.impl.StoreDescriptionBuilder;
import com.qfs.server.cfg.IDatastoreDescriptionConfig;
import com.quartetfs.fwk.format.impl.LocalDateParser;

/**
 * Spring configuration file that exposes the datastore
 * {@link IDatastoreSchemaDescription description}.
 *
 * @author ActiveViam
 *
 */
@Configuration
public class DatastoreDescriptionConfig implements IDatastoreDescriptionConfig {


	/*********************** Stores names **********************/
	public static final String STORE_RUSSIA2018 = "RussiaWorldCup2018";

	/********************* Stores fields ***********************/
	public static final String RUSSIA2018_GAME_ID = "gameId";
	public static final String RUSSIA2018_TEAM1_NAME = "Team1Name";
	public static final String RUSSIA2018_TEAM2_NAME = "Team2Name";
	public static final String RUSSIA2018_GAME_DATE = "GameDate";
	public static final String RUSSIA2018_GAME_TIME = "GameTime";
	public static final String RUSSIA2018_TEAM1_SCORE = "Team1Score";
	public static final String RUSSIA2018_TEAM2_SCORE = "Team2Score";

	/******************** Formatters ***************************/
	public static final String DATE_FORMAT = "localDate["+LocalDateParser.DEFAULT_PATTERN+"]";
	public static final String TIME_FORMAT = "localTime[HH:mm[:ss]]";

	@Bean
	public IStoreDescription russia2018StoreDescription() {
		return new StoreDescriptionBuilder().withStoreName(STORE_RUSSIA2018)
				.withField(RUSSIA2018_GAME_ID, INT).asKeyField()
				.withField(RUSSIA2018_TEAM1_NAME, STRING)
				.withField(RUSSIA2018_TEAM2_NAME, STRING)
				.withField(RUSSIA2018_GAME_DATE, DATE_FORMAT)
				.withField(RUSSIA2018_GAME_TIME, TIME_FORMAT)
				.withField(RUSSIA2018_TEAM1_SCORE, INT)
				.withField(RUSSIA2018_TEAM2_SCORE, INT)
				.build();
	}

	@Bean
	public Collection<IReferenceDescription> references(){
		final Collection<IReferenceDescription> references = new LinkedList<>();
		return references;
	}

	/**
	 *
	 * Provide the schema description of the datastore.
	 * <p>
	 * It is based on the descriptions of the stores in the datastore, the descriptions of the
	 * references between those stores, and the optimizations and constraints set on the schema.
	 *
	 * @return schema description
	 */
	@Override
	@Bean
	public IDatastoreSchemaDescription schemaDescription() {
		final Collection<IStoreDescription> stores = new LinkedList<>();
		stores.add(russia2018StoreDescription());
		return new DatastoreSchemaDescription(stores, references());
	}

}
