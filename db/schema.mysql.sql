-- db/schema.mysql.sql
-- MySQL 8.x schema for: Match traveler (TRAVELER) ↔ guide (GUIDE)
-- Designed to work smoothly in MySQL Workbench

-- Recommended charset/collation:
-- utf8mb4 + utf8mb4_0900_ai_ci (case-insensitive for email comparisons)

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Create database (optional)
-- CREATE DATABASE IF NOT EXISTS profiles_app
--   DEFAULT CHARACTER SET utf8mb4
--   DEFAULT COLLATE utf8mb4_0900_ai_ci;
-- USE profiles_app;

-- Drop order (optional for reset)
-- SET FOREIGN_KEY_CHECKS = 0;
-- DROP TABLE IF EXISTS review, message, match_event, `match`, guide_availability, trip,
--   profile_interest, interest, onboarding_answer, onboarding_question,
--   profile_location, location, profile, app_user;
-- SET FOREIGN_KEY_CHECKS = 1;

-- 1) Users
CREATE TABLE IF NOT EXISTS app_user (
  id            CHAR(36) PRIMARY KEY,                           -- UUID string
  email         VARCHAR(255) NULL,
  phone         VARCHAR(32) NULL,
  password_hash VARCHAR(255) NULL,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_app_user_email (email),
  UNIQUE KEY uq_app_user_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2) Profile
CREATE TABLE IF NOT EXISTS profile (
  id            CHAR(36) PRIMARY KEY,                           -- UUID string
  user_id       CHAR(36) NULL,

  type          ENUM('TRAVELER','GUIDE') NOT NULL,
  display_name  VARCHAR(120) NOT NULL,
  avatar_url    VARCHAR(2048) NULL,
  bio           TEXT NULL,
  locale        VARCHAR(20) NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_profile_user (user_id),
  KEY idx_profile_type (type),
  KEY idx_profile_name (display_name),

  CONSTRAINT fk_profile_user
    FOREIGN KEY (user_id) REFERENCES app_user(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  CONSTRAINT chk_profile_avatar_url
    CHECK (avatar_url IS NULL OR avatar_url REGEXP '^(https?://)')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3) Location
CREATE TABLE IF NOT EXISTS location (
  id          CHAR(36) PRIMARY KEY,
  country     VARCHAR(100) NOT NULL,
  region      VARCHAR(120) NULL,
  city        VARCHAR(120) NULL,
  place_id    VARCHAR(255) NULL,
  lat         DOUBLE NULL,
  lon         DOUBLE NULL,

  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_location_basic (country, region, city),
  KEY idx_location_country_city (country, city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4) Profile ↔ Location
CREATE TABLE IF NOT EXISTS profile_location (
  profile_id   CHAR(36) NOT NULL,
  location_id  CHAR(36) NOT NULL,
  kind         VARCHAR(30) NOT NULL DEFAULT 'PRIMARY',
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (profile_id, location_id, kind),

  CONSTRAINT fk_profile_location_profile
    FOREIGN KEY (profile_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_profile_location_location
    FOREIGN KEY (location_id) REFERENCES location(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 5) Onboarding questions
CREATE TABLE IF NOT EXISTS onboarding_question (
  id            CHAR(36) PRIMARY KEY,
  code          VARCHAR(64) NOT NULL,
  prompt        TEXT NOT NULL,
  profile_type  ENUM('TRAVELER','GUIDE') NULL,        -- NULL = both
  answer_kind   VARCHAR(30) NOT NULL DEFAULT 'TEXT',  -- TEXT/SINGLE_SELECT/MULTI_SELECT/NUMBER/JSON
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  sort_order    INT NOT NULL DEFAULT 0,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_onboarding_question_code (code),
  KEY idx_question_active_order (is_active, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 6) Onboarding answers
CREATE TABLE IF NOT EXISTS onboarding_answer (
  id            CHAR(36) PRIMARY KEY,
  profile_id    CHAR(36) NOT NULL,
  question_id   CHAR(36) NOT NULL,

  answer_text   TEXT NULL,
  answer_json   JSON NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_onboarding_answer (profile_id, question_id),
  KEY idx_answer_profile (profile_id),
  KEY idx_answer_question (question_id),

  CONSTRAINT fk_answer_profile
    FOREIGN KEY (profile_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_answer_question
    FOREIGN KEY (question_id) REFERENCES onboarding_question(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT chk_answer_has_value
    CHECK (answer_text IS NOT NULL OR answer_json IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 7) Interests
CREATE TABLE IF NOT EXISTS interest (
  id          CHAR(36) PRIMARY KEY,
  slug        VARCHAR(64) NOT NULL,
  label       VARCHAR(120) NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_interest_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS profile_interest (
  profile_id   CHAR(36) NOT NULL,
  interest_id  CHAR(36) NOT NULL,
  weight       TINYINT UNSIGNED NOT NULL DEFAULT 1,

  PRIMARY KEY (profile_id, interest_id),
  KEY idx_profile_interest_interest (interest_id),

  CONSTRAINT fk_profile_interest_profile
    FOREIGN KEY (profile_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_profile_interest_interest
    FOREIGN KEY (interest_id) REFERENCES interest(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  CONSTRAINT chk_interest_weight
    CHECK (weight BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 8) Trips (Traveler)
CREATE TABLE IF NOT EXISTS trip (
  id            CHAR(36) PRIMARY KEY,
  traveler_id   CHAR(36) NOT NULL,
  location_id   CHAR(36) NOT NULL,

  start_date    DATE NOT NULL,
  end_date      DATE NOT NULL,
  notes         TEXT NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_trip_traveler_dates (traveler_id, start_date, end_date),
  KEY idx_trip_location_dates (location_id, start_date, end_date),

  CONSTRAINT fk_trip_traveler
    FOREIGN KEY (traveler_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_trip_location
    FOREIGN KEY (location_id) REFERENCES location(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  CONSTRAINT chk_trip_dates
    CHECK (end_date >= start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 9) Guide availability
CREATE TABLE IF NOT EXISTS guide_availability (
  id          CHAR(36) PRIMARY KEY,
  guide_id    CHAR(36) NOT NULL,
  location_id CHAR(36) NULL,

  start_date  DATE NOT NULL,
  end_date    DATE NOT NULL,
  capacity    INT NOT NULL DEFAULT 1,

  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_avail_guide_dates (guide_id, start_date, end_date),
  KEY idx_avail_location_dates (location_id, start_date, end_date),

  CONSTRAINT fk_avail_guide
    FOREIGN KEY (guide_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_avail_location
    FOREIGN KEY (location_id) REFERENCES location(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  CONSTRAINT chk_availability_dates
    CHECK (end_date >= start_date),

  CONSTRAINT chk_availability_capacity
    CHECK (capacity >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 10) Match + events + messages
CREATE TABLE IF NOT EXISTS `match` (
  id            CHAR(36) PRIMARY KEY,
  traveler_id   CHAR(36) NOT NULL,
  guide_id      CHAR(36) NOT NULL,
  trip_id       CHAR(36) NULL,

  status        ENUM('PENDING','ACCEPTED','REJECTED','CANCELLED') NOT NULL DEFAULT 'PENDING',
  score         DECIMAL(6,3) NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_match_unique (traveler_id, guide_id, trip_id),
  KEY idx_match_traveler_status (traveler_id, status, created_at),
  KEY idx_match_guide_status (guide_id, status, created_at),
  KEY idx_match_trip (trip_id),

  CONSTRAINT fk_match_traveler
    FOREIGN KEY (traveler_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_match_guide
    FOREIGN KEY (guide_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_match_trip
    FOREIGN KEY (trip_id) REFERENCES trip(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  CONSTRAINT chk_match_roles
    CHECK (traveler_id <> guide_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS match_event (
  id          CHAR(36) PRIMARY KEY,
  match_id    CHAR(36) NOT NULL,
  actor_id    CHAR(36) NULL,
  event_type  VARCHAR(30) NOT NULL, -- CREATED/ACCEPTED/REJECTED/CANCELLED
  payload     JSON NULL,

  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_match_event_match_time (match_id, created_at),

  CONSTRAINT fk_match_event_match
    FOREIGN KEY (match_id) REFERENCES `match`(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_match_event_actor
    FOREIGN KEY (actor_id) REFERENCES profile(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS message (
  id          CHAR(36) PRIMARY KEY,
  match_id    CHAR(36) NOT NULL,
  sender_id   CHAR(36) NULL,

  kind        ENUM('TEXT','SYSTEM') NOT NULL DEFAULT 'TEXT',
  body        TEXT NULL,
  payload     JSON NULL,

  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_message_match_time (match_id, created_at),

  CONSTRAINT fk_message_match
    FOREIGN KEY (match_id) REFERENCES `match`(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_message_sender
    FOREIGN KEY (sender_id) REFERENCES profile(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  CONSTRAINT chk_message_has_content
    CHECK (body IS NOT NULL OR payload IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 11) Reviews
CREATE TABLE IF NOT EXISTS review (
  id            CHAR(36) PRIMARY KEY,
  match_id      CHAR(36) NOT NULL,
  reviewer_id   CHAR(36) NOT NULL,
  reviewee_id   CHAR(36) NOT NULL,

  rating        TINYINT NOT NULL,
  comment       TEXT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_review_unique (match_id, reviewer_id),
  KEY idx_review_reviewee (reviewee_id, created_at),

  CONSTRAINT fk_review_match
    FOREIGN KEY (match_id) REFERENCES `match`(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_review_reviewer
    FOREIGN KEY (reviewer_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_review_reviewee
    FOREIGN KEY (reviewee_id) REFERENCES profile(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT chk_review_rating
    CHECK (rating BETWEEN 1 AND 5),

  CONSTRAINT chk_review_roles
    CHECK (reviewer_id <> reviewee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;