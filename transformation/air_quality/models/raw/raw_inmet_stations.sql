with source as (
    select * from air_quality_raw.inmet_stations
),

renamed as (
    select
        station_id,
        station_name,
        upper(state)             as state,
        cast(latitude as double) as latitude,
        cast(longitude as double) as longitude,
        cast(altitude as double) as altitude,
        station_type
    from source
)

select * from renamed