create table users (
    id           bigint unsigned not null auto_increment,
    email        varchar(320) unique,
    phone        varchar(32) unique,
    display_name varchar(120),
    role         enum('traveler','guide') not null,
    created_at   timestamp not null default current_timestamp,
    updated_at   timestamp not null default current_timestamp on update current_timestamp,
    primary key (id)
) engine=InnoDB;

create table profiles (
    user_id        bigint unsigned not null,
    -- comunes
    pace           tinyint unsigned null,    -- 0..10
    photo_vibe     varchar(80) null,
    notes          text null,

    -- traveler-only (nullable)
    travel_style    varchar(40) null,
    group_pref      varchar(40) null,
    planning_level  tinyint unsigned null,   -- 1..5
    transport       varchar(40) null,

    -- guide-only (nullable)
    experience_level varchar(40) null,
    guide_style       varchar(60) null,
    group_size        varchar(20) null,

    -- raw answers for audit/UI
    answers_json    json not null,
    version         varchar(16) not null default 'v1',

    created_at      timestamp not null default current_timestamp,
    updated_at      timestamp not null default current_timestamp on update current_timestamp,

    primary key (user_id),
    constraint fk_profiles_user foreign key (user_id) references users(id) on delete cascade,

    -- validaciones suaves (MySQL 8 enforces CHECK en la práctica)
    constraint chk_pace check (pace is null or pace between 0 and 10),
    constraint chk_planning check (planning_level is null or planning_level between 1 and 5)
) engine=InnoDB;
