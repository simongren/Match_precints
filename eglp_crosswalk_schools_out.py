    #Eckert, Gvirtz, Liang, Peters, 2020
    #"A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790"
    #www.fpeckert.me/eglp

    ## A generic code to construct your own crosswalk, from two shapefiles

    import pandas as pd
    import geopandas as gpd
    import os
    import time

    df_weights=[]
    years =['2014','2010','2006','2002']
    mun_diff=[]
    for year in years:

        start = time.time()  ## for testing purposes
        ## defining variables - change the things in ALL_CAPS
        origin_path = 'C:/Users/xlunsi/Desktop/Projects/School_openings/Data/shapefiles/'
        origin_fname = 'districs_clean_dissolve2018.shp'
        origin_geoid = 'VD_2018'

        destination_path = 'C:/Users/xlunsi/Desktop/Projects/School_openings/Data/shapefiles/'
        destination_fname = 'districs_clean_dissolve'+year+'.shp'
        destination_geoid = 'VD_'+year


        output_fname = 'weights_2018_'+year+'.csv'


        ## read in starting shapefile
        os.chdir(origin_path)
        shp_origin = gpd.GeoDataFrame.from_file(origin_fname)
        shp_origin['area_base'] = shp_origin.area

        ## read in ending shapefile
        os.chdir(destination_path)
        shp_destination = gpd.GeoDataFrame.from_file(destination_fname)


        ## intersecting the file
        intersect = gpd.overlay(shp_origin, shp_destination, how = 'intersection',keep_geom_type=False)
        intersect['area'] = intersect.area

        ## computing weights
        intersect['weight'] = intersect['area'] / intersect['area_base']

        # Removing intersection areas smaller then 10 m2
        intersect = intersect[intersect['area'] > 10]

        # Assuming the columns are in string format, you can use str.slice to get the first 4 characters
        condition = intersect['VD_2018'].str[:4] != intersect['VD_'+year].str[:4]
        remove=intersect[condition]
        # Use the condition to subset the DataFrame
        mun_diff.append(remove)

        condition_keep=intersect['VD_2018'].str[:4] == intersect['VD_'+year].str[:4]
        intersect=intersect[condition_keep]

        ## renormalizing weights - this isn't necesary, but without it, if the shapefiles do not perfectly line up where they should, you may lose small fractions of area here and there
        reweight = intersect.groupby(origin_geoid)['weight'].sum().reset_index()
        reweight['new_weight'] = reweight['weight']
        reweight = reweight.drop('weight', axis = 1)

        intersect = intersect.merge(reweight, left_on = origin_geoid, right_on = origin_geoid)
        intersect['weight'] = intersect['weight'] / intersect['new_weight']

        intersect = intersect.drop('new_weight', axis =1)


        ## keeping only relevant columns - again isn't necessary, but will help trim down the size of the crosswalk at the end
        output = intersect[[origin_geoid, destination_geoid, 'weight']]
        output.to_csv(output_fname, index = False)
        # Use the .rename() method to rename the column
        output = output.rename(columns={destination_geoid: 'VD'})
        output['year'] = int(year)

        ## saving output
        df_weights.append(output)

        print(year, time.time() - start)

    df_weights_all = pd.concat(df_weights)
    df_weights_all.to_csv('all_weights.csv', index=False)
