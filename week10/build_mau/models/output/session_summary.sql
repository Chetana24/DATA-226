with session_duration as (
    select
        s.session_id,
        s.user_id,
        s.start_time,
        s.end_time,
        timestampdiff(second, s.start_time, s.end_time) as duration_seconds
    from {{ ref('session_timestamp') }} as s
),

user_channel as (
    select
        uc.session_id,
        uc.user_id,
        uc.channel
    from {{ ref('user_session_channel') }} as uc
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
