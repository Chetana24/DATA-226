with session_time as (
    select
        session_id,
        user_id,
        start_time,
        end_time
    from {{ source('raw_data', 'user_session_channel') }} 
)

select * from session_time
