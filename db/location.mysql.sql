SELECT
  g.id AS guide_id,
  g.display_name,
  l.country, l.city,
  ga.start_date, ga.end_date
FROM trip t
JOIN location l ON l.id = t.location_id
JOIN guide_availability ga
  ON ga.location_id = t.location_id
 AND ga.start_date <= t.end_date
 AND ga.end_date >= t.start_date
JOIN profile g
  ON g.id = ga.guide_id
 AND g.type = 'GUIDE'
WHERE t.id = ?  -- trip_id
ORDER BY ga.start_date ASC;