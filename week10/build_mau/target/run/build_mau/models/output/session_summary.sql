
  
    

        create or replace transient table dev.analytics.session_summary
         as
        (with  __dbt__cte__session_timestamp as (
with session_time as (
    select
        session_id,
        user_id,
        start_time,
        end_time
    from dev.raw_data.user_session_channel 
)

select * from session_time
),  __dbt__cte__user_session_channel as (
with user_channel_data as (
    select
        user_id,
        channel,
        session_id
    from dev.raw_data.session_timestamp 
)

select * from user_channel_data
), session_duration as (
    select
        s.session_id,
        s.user_id,
        s.start_time,
        s.end_time,
        timestampdiff(second, s.start_time, s.end_time) as duration_seconds
    from __dbt__cte__session_timestamp as s
),

user_channel as (
    select
        uc.session_id,
        uc.user_id,
        uc.channel
    from __dbt__cte__user_session_channel as uc
)

select
    sd.session_id,
    sd.user_id,
    uc.channel,
    sd.start_time,
    sd.end_time,
    sd.duration_seconds
from session_duration sd
join user_channel uc on sd.session_id = uc.session_id
        );
      
  