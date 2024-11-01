-- snapshots/snapshot_session_summary.sql
{% snapshot snapshot_session_summary %}

{{
    config(
        target_schema='snapshots',
        unique_key='session_id',
        strategy='timestamp',
        updated_at='end_time'
    )
}}

select * from {{ ref('session_summary') }}

{% endsnapshot %}
