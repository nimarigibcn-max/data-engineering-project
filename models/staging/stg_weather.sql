with source as (

    select raw_data
    from WEATHER_DB.RAW.WEATHER_RAW

),

flattened as (

    select
        f.value::date                                           as date,
        GET(raw_data:daily.temperature_2m_max, f.index)::float as temperature_max_c,
        GET(raw_data:daily.temperature_2m_min, f.index)::float as temperature_min_c,
        COALESCE(GET(raw_data:daily.precipitation_sum, f.index)::float, 0) as precipitation_mm
    from source,
    lateral flatten(input => raw_data:daily.time) as f

),

deduplicated as (

    select
        date,
        avg(temperature_max_c) as temperature_max_c,
        avg(temperature_min_c) as temperature_min_c,
        avg(precipitation_mm)  as precipitation_mm
    from flattened
    where date is not null
      and temperature_max_c is not null
    group by date

)

select * from deduplicated
order by date