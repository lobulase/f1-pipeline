select
    Driver,
    Race,
    Round,
    Compound,
    round(avg(LapTimeSeconds), 3) as avg_lap_seconds,
    round(min(LapTimeSeconds), 3) as best_lap_seconds,
    count(*) as total_laps
from {{ source('f1_raw', 'laps') }}
where LapTimeSeconds is not null
  and LapTimeSeconds > 60
group by Driver, Race, Round, Compound
order by Race, avg_lap_seconds