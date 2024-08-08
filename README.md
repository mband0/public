### Database Schema: `us`

Our database schema, named `us`, is organized into several tables and views that store and aggregate data about members of Congress and legislation. Here’s a detailed breakdown:

### Tables

1. **legislation**
   - **Columns:** leg_id, number, title, congress, type, intro_date, policy_area, origin_chamber, latest_action, action_date, num_actions, num_amendments, num_committees, num_com_reports, sponsor_id, sponsor_name, num_cosponsors, subjects, related, row_ct_dt, row_ct_user
   - **Description:** Stores detailed information about each piece of legislation, including its ID, title, type, policy area, sponsor, and related actions.

2. **members**
   - **Columns:** member_id, district, full_name, party_name, state, chamber, end_year, start_year, first_name, last_name, middle_name, birth_year, member_id_key, nickname, image, row_ct_dt, row_ct_user
   - **Description:** Contains personal and professional information about each member of Congress.

3. **leg_actions**
   - **Columns:** leg_id, date, action, type, row_ct_dt, row_ct_user
   - **Description:** Tracks the actions taken on each piece of legislation, such as amendments and votes.

4. **leg_subjects**
   - **Columns:** leg_id, subject, row_ct_dt, row_ct_user
   - **Description:** Associates legislation with specific subjects.

5. **leg_relationships**
   - **Columns:** leg_id, related_leg_id, identifier, rel_type, row_ct_dt, row_ct_user
   - **Description:** Stores relationships between pieces of legislation, such as amendments or companion bills.

6. **leg_cosponsors**
   - **Columns:** leg_id, sponsor_id, name, row_ct_dt, row_ct_user
   - **Description:** Lists the cosponsors of each piece of legislation.

7. **leg_pro_cons**
   - **Columns:** leg_id, subject, policy_area, pro_con, pro_con_title, impact_score, impact_reason, source, pro_con_id, row_ct_dt, row_ct_user
   - **Description:** Stores pros and cons evaluations for each piece of legislation.

8. **pro_con_scoring**
   - **Columns:** pro_con_id, impact_score, impact_reason, scope_score, scope_reason, intensity_score, intensity_reason, duration_score, duration_reason, irreversibility_score, irreversibility_reason, probability_score, probability_reason, row_ct_dt, row_ct_user
   - **Description:** Provides detailed scoring for each pro and con evaluation.

9. **member_sponsored_leg**
   - **Columns:** member_id, intro_date, congress, leg_id, number, title, policy_area, type, latest_action, action_date, row_ct_dt, row_ct_user
   - **Description:** Lists the legislation sponsored by each member.

10. **member_cosponsored_leg**
    - **Columns:** member_id, intro_date, congress, leg_id, number, title, policy_area, type, latest_action, action_date, row_ct_dt, row_ct_user
    - **Description:** Lists the legislation cosponsored by each member.

11. **leg_texts**
    - **Columns:** leg_id, date, format, text, type, row_ct_dt, row_ct_user
    - **Description:** Stores the text of legislation in various formats (HTML, XML, PDF).

### Views

1. **vw_bills**
   - **Description:** Filters data from the `legislation` table for HR and S bill types, excluding resolutions.

2. **vw_laws**
   - **Description:** Filters data from the `legislation` table to focus on legislation that became law, using the `leg_actions` table.

3. **vw_member_cosponsored_bills**
   - **Description:** Filters data from the `member_cosponsored_leg` table joined with the `legislation` table for HR and S bill types.

4. **vw_member_sponsored_bills**
   - **Description:** Filters data from the `member_sponsored_leg` table joined with the `legislation` table for HR and S bill types.

5. **vw_member_policy_area_sponsorship**
   - **Description:** Aggregates data to show the percentage of bills sponsored by each member in different policy areas, compares it to the average percentage, and calculates a sponsorship ratio.

6. **vw_member_subject_sponsorship**
   - **Description:** Aggregates data to show the percentage of bills sponsored by each member for different subjects, compares it to the average percentage, and calculates a sponsorship ratio.

7. **mvw_member_subject_cosponsorship** (Materialized View)
   - **Description:** Aggregates data to show the percentage of bills cosponsored by each member for different subjects, compares it to the average percentage, and calculates a cosponsorship ratio.

8. **vw_member_policy_area_cosponsorship**
   - **Description:** Aggregates data to show the percentage of bills cosponsored by each member in different policy areas, compares it to the average percentage, and calculates a cosponsorship ratio.

9. **vw_member_subject_activity**
   - **Description:** Combines sponsorship and cosponsorship ratios for members across various subjects and calculates an overall activity score.

10. **vw_member_policy_area_activity**
    - **Description:** Combines sponsorship and cosponsorship ratios for members across various policy areas and calculates an overall activity score.

11. **vw_member_bill_conversion**
    - **Description:** Provides statistics on the legislative effectiveness of members by showing the total bills sponsored, the number of those bills that became law, and the percentage of sponsored bills that became law.

12. **mvw_member_policy_area_impacts** (Materialized View)
    - **Description:** Calculates the cumulative net positive impact of legislation sponsored by each member in various policy areas, derived from pros and cons scoring.

13. **mvw_mem_avg_bill_support** (Materialized View)
    - **Description:** Calculates the average number of cosponsors for bills sponsored by each member, reflecting average support for their legislation.
