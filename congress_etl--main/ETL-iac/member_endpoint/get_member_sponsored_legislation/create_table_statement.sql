CREATE TABLE IF NOT EXISTS "us_stg.member_sponsored_legislation" (
  "congress" bigint,
  "introducedDate" text,
  "latestAction" json,
  "number" text,
  "policyArea" json,
  "title" text,
  "type" text,
  "url" text
);