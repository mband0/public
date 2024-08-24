CREATE TABLE IF NOT EXISTS "us_stg.member_cosponsored_legislation" (
  "congress" bigint,
  "introduceddate" text,
  "latestaction" json,
  "number" text,
  "policyarea" json,
  "title" text,
  "type" text,
  "url" text
);