select
    Race,
    Round,
    Year,
    count(*) as total_laps,
    round(avg(LapTimeSeconds), 3) as avg_lap_seconds,
    round(min(LapTimeSeconds), 3) as fastest_lap
from {{ source('f1_raw', 'laps') }}
where LapTimeSeconds is not null
  and LapTimeSeconds > 60
group by Race, Round, Year
order by Year, Round