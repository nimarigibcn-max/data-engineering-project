with staging as (

    select * from {{ ref('stg_weather') }}

),

final as (

    select
        date,
        temperature_max_c,
        temperature_min_c,
        round(temperature_max_c - temperature_min_c, 1)     as temperature_range_c,
        round((temperature_max_c + temperature_min_c) / 2, 1) as temperature_avg_c,
        precipitation_mm,
        case
            when precipitation_mm = 0    then 'Dry'
            when precipitation_mm < 5    then 'Light rain'
            when precipitation_mm < 20   then 'Moderate rain'
            else 'Heavy rain'
        end                                                  as precipitation_category
    from staging

)

select * from final
order by date