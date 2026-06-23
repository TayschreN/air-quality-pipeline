with source as (
    select * from air_quality_raw.openaq_stations
),

renamed as (
    select
        cast(location_id as bigint)      as location_id,
        location_name,
        city,
        country,
        lower(parameter)                 as parameter,
        unit,
        cast(latitude as double)         as latitude,
        cast(longitude as double)        as longitude,
        is_active,
        last_updated                     as last_updated_at
    from source
    where country = 'BR'
)

select * from renamed