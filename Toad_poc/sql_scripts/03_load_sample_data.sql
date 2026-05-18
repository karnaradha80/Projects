-- Step 3: Load sample data into Azure SQL tables
-- Matches the sample_data\ CSV files

-- ODS log: today's date (simulates data load completed)
TRUNCATE TABLE MAXRPD.T_ODS_LOG;
INSERT INTO MAXRPD.T_ODS_LOG (ems) VALUES (CAST(GETDATE() AS DATE));

-- Dimension: work orders (10 root + 10 gas-prevented)
TRUNCATE TABLE abcbimart.dim_work_orders;
INSERT INTO abcbimart.dim_work_orders (id, work_order_number, reported_date_time) VALUES
(1,  'WO-1001', '2026-05-13 08:15:00'),
(2,  'WO-1002', '2026-05-13 09:30:00'),
(3,  'WO-1003', '2026-05-13 11:00:00'),
(4,  'WO-1004', '2026-05-13 13:45:00'),
(5,  'WO-1005', '2026-05-13 15:20:00'),
(6,  'WO-1006', '2026-05-12 07:00:00'),
(7,  'WO-1007', '2026-05-12 10:10:00'),
(8,  'WO-1008', '2026-05-12 14:30:00'),
(9,  'WO-1009', '2026-04-10 08:00:00'),
(10, 'WO-1010', '2026-04-10 12:00:00'),
(11, 'WO-2001', '2026-05-13 08:15:00'),
(12, 'WO-2002', '2026-05-13 09:30:00'),
(13, 'WO-2003', '2026-05-13 11:00:00'),
(14, 'WO-2004', '2026-05-13 13:45:00'),
(15, 'WO-2005', '2026-05-13 15:20:00'),
(16, 'WO-2006', '2026-05-12 07:00:00'),
(17, 'WO-2007', '2026-05-12 10:10:00'),
(18, 'WO-2008', '2026-05-12 14:30:00'),
(19, 'WO-2009', '2026-04-10 08:00:00'),
(20, 'WO-2010', '2026-04-10 12:00:00');

-- Dimension: organisation
TRUNCATE TABLE abcbimart.dim_organisation;
INSERT INTO abcbimart.dim_organisation (id, network, ldz, depot_work_group) VALUES
(1,  'Network_A', 'LDZ_01', 'DEPOT_A'),
(2,  'Network_A', 'LDZ_01', 'DEPOT_B'),
(3,  'Network_A', 'LDZ_01', 'DEPOT_C'),
(4,  'Network_A', 'LDZ_02', 'DEPOT_D'),
(5,  'Network_A', 'LDZ_02', 'DEPOT_E'),
(6,  'Network_B', 'LDZ_03', 'DEPOT_F'),
(7,  'Network_B', 'LDZ_03', 'DEPOT_G'),
(8,  'Network_B', 'LDZ_03', 'DEPOT_H'),
(9,  'Network_A', 'LDZ_01', 'DEPOT_I'),
(10, 'Network_A', 'LDZ_02', 'DEPOT_J');

-- Dimension: addresses
TRUNCATE TABLE abcbimart.dim_addresses;
INSERT INTO abcbimart.dim_addresses (id, display_address) VALUES
(1,  '1 Sample Street, Town_A, AA1 1AA'),
(2,  '2 Sample Street, Town_B, BB2 2BB'),
(3,  '3 Sample Street, Town_C, CC3 3CC'),
(4,  '4 Sample Street, Town_D, DD4 4DD'),
(5,  '5 Sample Street, Town_E, EE5 5EE'),
(6,  '6 Sample Street, Town_F, FF6 6FF'),
(7,  '7 Sample Street, Town_G, GG7 7GG'),
(8,  '8 Sample Street, Town_H, HH8 8HH'),
(9,  '9 Sample Street, Town_I, II9 9II'),
(10, '10 Sample Street, Town_J, JJ0 0JJ');

-- Dimension: calendar
TRUNCATE TABLE abcbimart.dim_calendar;
INSERT INTO abcbimart.dim_calendar (id, date_disp_1, date_oracle) VALUES
(1, '13/05/2026', '2026-05-13'),
(2, '12/05/2026', '2026-05-12'),
(3, '11/05/2026', '2026-05-11'),
(4, '10/04/2026', '2026-04-10'),
(5, '01/04/2026', '2026-04-01'),
(6, '01/03/2026', '2026-03-01'),
(7, '01/02/2026', '2026-02-01'),
(8, '01/01/2026', '2026-01-01');

-- Dimension: time
TRUNCATE TABLE abcbimart.dim_time;
INSERT INTO abcbimart.dim_time (id, hour_24_minute) VALUES
(1,  '08:30:00'),
(2,  '10:45:00'),
(3,  '12:00:00'),
(4,  '14:15:00'),
(5,  '16:30:00'),
(6,  '09:00:00'),
(7,  '11:20:00'),
(8,  '13:50:00'),
(9,  '18:00:00'),
(10, '20:45:00');

-- Fact table: gas escape incidents
TRUNCATE TABLE abcbimart.fct_gas_escapes_v;
INSERT INTO abcbimart.fct_gas_escapes_v
    (id, dwor_id_root, dwor_id_gas_prevented, dorg_id_root, dadr_id_root, dcal_id_gas_prevented_date, dtim_id_gas_prevented_time, latest)
VALUES
(1,  1,  11, 1,  1,  1, 1,  'Y'),
(2,  2,  12, 2,  2,  1, 2,  'Y'),
(3,  3,  13, 3,  3,  1, 3,  'Y'),
(4,  4,  14, 4,  4,  1, 4,  'Y'),
(5,  5,  15, 5,  5,  1, 5,  'Y'),
(6,  6,  16, 6,  6,  2, 6,  'Y'),
(7,  7,  17, 7,  7,  2, 7,  'Y'),
(8,  8,  18, 8,  8,  2, 8,  'Y'),
(9,  9,  19, 9,  9,  4, 9,  'Y'),
(10, 10, 20, 10, 10, 4, 10, 'Y');

-- ── Config Data ────────────────────────────────────────────────────────────────

-- Config: reports
DELETE FROM config.report_email;
DELETE FROM config.report;
DBCC CHECKIDENT ('config.report',       RESEED, 0);
DBCC CHECKIDENT ('config.report_email', RESEED, 0);

INSERT INTO config.report (report_name, description, schedule, output_format, is_active) VALUES
('BC_BIMIO_267_Daily', 'BIMIO 267 - 12 Hour Prevented Daily (MTD, YTD)', 'Daily', 'CSV', 'Y');

-- Config: email distribution for BC_BIMIO_267_Daily (report_id = 1)
INSERT INTO config.report_email (report_id, email_address, email_type, recipient_group, is_active) VALUES
-- Operations teams (TO) — receive the daily report
(1, 'ops.depot_a@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_b@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_c@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_d@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_e@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_f@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_g@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_h@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
(1, 'ops.depot_i@abc.co.uk',       'TO',  'OPERATIONS',  'Y'),
-- BI team (BCC) — receive all report emails silently
(1, 'buin@abc.co.uk',              'BCC', 'BI_TEAM',     'Y'),
(1, 'bi.support@abc.co.uk',        'BCC', 'BI_TEAM',     'Y'),
-- Alert only (TO) — receive ODS not-refreshed alert, CC on report email
(1, 'manager.name1@abc.co.uk',     'CC',  'ALERT_ONLY',  'Y'),
(1, 'manager.name2@abc.co.uk',     'CC',  'ALERT_ONLY',  'Y');
