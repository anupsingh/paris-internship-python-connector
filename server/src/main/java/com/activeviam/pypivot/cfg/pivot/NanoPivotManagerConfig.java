/*
 * (C) ActiveViam 2018
 * ALL RIGHTS RESERVED. This material is the CONFIDENTIAL and PROPRIETARY
 * property of Quartet Financial Systems Limited. Any unauthorized use,
 * reproduction or transfer of this material is strictly prohibited
 */
package com.activeviam.pypivot.cfg.pivot;

import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.RUSSIA2018_GAME_DATE;
import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.RUSSIA2018_GAME_TIME;
import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.RUSSIA2018_TEAM1_NAME;
import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.RUSSIA2018_TEAM1_SCORE;
import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.RUSSIA2018_TEAM2_NAME;
import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.RUSSIA2018_TEAM2_SCORE;
import static com.activeviam.pypivot.cfg.datastore.DatastoreDescriptionConfig.STORE_RUSSIA2018;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.activeviam.builders.StartBuilding;
import com.activeviam.copper.builders.BuildingContext;
import com.activeviam.copper.builders.dataset.Datasets.Dataset;
import com.activeviam.copper.columns.Columns;
import com.activeviam.desc.build.ICanBuildCubeDescription;
import com.activeviam.desc.build.ICubeDescriptionBuilder.INamedCubeDescriptionBuilder;
import com.activeviam.desc.build.dimensions.ICanStartBuildingDimensions;
import com.qfs.desc.IDatastoreSchemaDescription;
import com.qfs.server.cfg.IActivePivotManagerDescriptionConfig;
import com.quartetfs.biz.pivot.cube.hierarchy.ILevelInfo.LevelType;
import com.quartetfs.biz.pivot.definitions.IActivePivotInstanceDescription;
import com.quartetfs.biz.pivot.definitions.IActivePivotManagerDescription;
import com.quartetfs.biz.pivot.definitions.ISelectionDescription;

/**
 * @author ActiveViam
 *
 */
@Configuration
public class NanoPivotManagerConfig implements IActivePivotManagerDescriptionConfig {

	public static final String MANAGER_NAME = "NanoPivotManager";
	public static final String CATALOG_NAME = "NanoPivotCatalog";
	public static final String SCHEMA_NAME = "NanoPivotSchema";
	public static final String CUBE_NAME = "NanoPivotCube";

	/* **************************************** */
	/* Levels, hierarchies and dimensions names */
	/* **************************************** */
	public static final String GAMES_DIMENSION = "Games";
	public static final String SCORES_DIMENSION = "Scores";
	public static final String DATE_TIME_DIMENSION = "Date Time";

	/* ************************* */
	/* Measures names */
	/* ************************* */
	public static final String COUNTRIBUTORS_COUNT_ALIAS = "Number of Games";
	public static final String TOTAL_SCORES = "Total scores";
	public static final String AVERAGE_SCORE = "Average score per game";
	
	/* ********** */
	/* Formatters */
	/* ********** */
	public static final String DOUBLE_FORMATTER_ONE_DECIMAL = "DOUBLE[##.#]";


	/** The datastore schema {@link IDatastoreSchemaDescription description}. */
	@Autowired
	protected IDatastoreSchemaDescription datastoreDescription;

	@Override
	@Bean
	public IActivePivotManagerDescription managerDescription() {
		
		return StartBuilding.managerDescription(MANAGER_NAME)
				.withCatalog(CATALOG_NAME)
				.containingAllCubes()
				.withSchema(SCHEMA_NAME)
				.withSelection(createNanoPivotSchemaSelectionDescription(this.datastoreDescription))
				.withCube(createCubeDescription())
				.build();
	}
	
	/**
	 * Creates the {@link ISelectionDescription} for NanoPivot Schema.
	 * 
	 * @param datastoreDescription : The datastore description
	 * @return The created selection description
	 */
	public static ISelectionDescription createNanoPivotSchemaSelectionDescription(
			final IDatastoreSchemaDescription datastoreDescription) {
		return StartBuilding.selection(datastoreDescription)
				.fromBaseStore(STORE_RUSSIA2018)
				.withAllReachableFields()
				.build();
	}
	
	/**
	 * Creates the cube description.
	 * @return The created cube description
	 */
	public static IActivePivotInstanceDescription createCubeDescription() {
		return configureCubeBuilder(StartBuilding.cube(CUBE_NAME)).build();
	}

	/**
	 * Configures the given builder in order to created the cube description.
	 *
	 * @param builder The builder to configure
	 * @return The configured builder
	 */
	public static ICanBuildCubeDescription<IActivePivotInstanceDescription> configureCubeBuilder(
			final INamedCubeDescriptionBuilder builder){
		
		return builder
				.withDimensions(NanoPivotManagerConfig::dimensions)
				
				//Suggestion : PostProcesser definitions can be added here
				
				.withDescriptionPostProcessor(
						StartBuilding.copperCalculations()
							.withDefinition(NanoPivotManagerConfig::coPPerCalculations)
							.build()
					)
				;
	}


	/**
	 * Adds the dimensions descriptions to the input
	 * builder.
	 *
	 * @param builder The cube builder
	 * @return The builder for chained calls
	 */
	public static ICanBuildCubeDescription<IActivePivotInstanceDescription> dimensions (ICanStartBuildingDimensions builder) {
		
		return builder
				.withDimension(GAMES_DIMENSION)
					.withHierarchyOfSameName()
						.withLevels(RUSSIA2018_TEAM1_NAME, RUSSIA2018_TEAM2_NAME)
						
				.withDimension(SCORES_DIMENSION)
					.withSingleLevelHierarchies(RUSSIA2018_TEAM1_SCORE, RUSSIA2018_TEAM2_SCORE)
						
				.withDimension(DATE_TIME_DIMENSION)
					.withHierarchyOfSameName()
						.withLevel(RUSSIA2018_GAME_DATE)
							.withType(LevelType.TIME)
							.withFormatter("DATE[yyyy-MM-dd]")
						.withLevel(RUSSIA2018_GAME_TIME)
							.withType(LevelType.TIME)
							.withFormatter("EPOCH[HH:mm:ss]")
				;
	}

	/* ******************* */
	/* Measures definition */
	/* ******************* */
	
	/**
	 * The CoPPer calculations to add to the cube
	 * @param context The context with which to build the calculations.
	 */
	public static void coPPerCalculations(BuildingContext context) {
		NanoPivotManagerConfig.someAggregatedMeasures(context).publish();
	}

	
	/**
	 * Creates aggregated measures.
	 *
	 * @param context The CoPPer build context.
	 *
	 * @return The Dataset of the aggregated measures.
	 */		
	protected static Dataset someAggregatedMeasures(final BuildingContext context) {
		
		return context.createDatasetFromFacts()
				.agg(
						Columns.count().as(COUNTRIBUTORS_COUNT_ALIAS)
					)
				.withColumn(TOTAL_SCORES, Columns.col(RUSSIA2018_TEAM1_SCORE).plus(Columns.col(RUSSIA2018_TEAM2_SCORE)))
				.agg(
						Columns.avg(TOTAL_SCORES).as(AVERAGE_SCORE).withFormatter(DOUBLE_FORMATTER_ONE_DECIMAL),
						Columns.sum(TOTAL_SCORES).as(TOTAL_SCORES)
					)
				;
		
	}


}
