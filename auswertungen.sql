select * from mqtt_logger order by logtime DESC;

select count(*) from mqtt_logger;

select * from mqtt_logger where payload like '%counter%' order by logtime desc;

select * from mqtt_logger where payload like '%counter%' and logtime > '2016-08-13 18:07:32.007781'
order by logtime desc;

/* left join variante */
SELECT
  a.payload :: JSON ->> 'counter',
  b.c
FROM mqtt_logger a
  LEFT JOIN (SELECT b.payload :: JSON ->> 'counter' "c"
             FROM mqtt_logger b
             WHERE b.topic = '/from_device/status' AND b.logtime >= '2016-08-13 18:07:32.007781') b
    ON a.payload :: JSON ->> 'counter' = a.payload :: JSON ->> 'counter'
WHERE a.topic = '/to/switch' AND a.logtime >= '2016-08-13 18:07:32.007781'
      and b.c is null;

/* not in variante */
select a.payload::json->>'counter' from mqtt_logger a
where  a.topic = '/to/switch' and a.logtime >= '2016-08-13 18:07:32.007781'
       and a.payload::json->>'counter' not in
           (select b.payload::json->>'counter' from mqtt_logger b WHERE
             b.topic = '/from_device/status'
             and b.payload::json->>'counter' is NOT null
             and b.logtime >= '2016-08-13 18:07:32.007781');

create table t1 as (SELECT a.payload :: JSON ->> 'counter' "c", a.topic
                    FROM mqtt_logger a
                    WHERE a.topic = '/to/switch' and a.logtime >= '2016-08-09 02:43:11.509745'
);

insert into t1 (SELECT a.payload :: JSON ->> 'counter' "c", a.topic
                FROM mqtt_logger a
                WHERE a.topic = '/from_device/status' and a.logtime >= '2016-08-09 02:43:11.509745');

select c from t1 WHERE t1.topic = '/to/switch' and c NOT IN (SELECT t1.c FROM t1 WHERE t1.topic = '/from_device/status');

select t1.c, t2.c from t1 left join (SELECT c from t1 where t1.topic = '/from_device/status') t2
    on t1.c = t2.c where t1.topic = '/to/switch' and t2.c is null;

select t1.c from t1 where t1.topic = '/to/switch' or t1.topic = '/from_device/status';

select * from t1 where c is null



CREATE TABLE a AS
  (select a.payload::json->>'counter' "c" from mqtt_logger a
  where  a.topic = '/to/switch' and a.logtime >= '2016-08-09 02:43:11.509745');

CREATE TABLE b AS
  (select b.payload::json->>'counter' "c" from mqtt_logger b WHERE
    b.topic = '/from_device/status'
    and b.logtime >= '2016-08-09 02:43:11.509745');

select a.c from a where a.c NOT in (SELECT b.c from b WHERE c is not null);

select * from mqtt_logger a
where  a.topic = '/to/switch' and a.logtime >= '2016-08-09 02:43:11.509745';

select c FROM a
EXCEPT
SELECT c from b;

SELECT a.c, b.c from a left join b on a.c = b.c WHERE b.c is null;