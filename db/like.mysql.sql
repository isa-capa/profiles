SELECT
  g.id AS guide_id,
  COUNT(*) AS shared_interests
FROM profile_interest pi_t
JOIN profile_interest pi_g
  ON pi_g.interest_id = pi_t.interest_id
JOIN profile g
  ON g.id = pi_g.profile_id
 AND g.type = 'GUIDE'
WHERE pi_t.profile_id = ?  -- traveler_profile_id
GROUP BY g.id
ORDER BY shared_interests DESC, g.id;