ALTER TABLE muk_dms_system_data RENAME TO muk_dms_data_system;

ALTER TABLE muk_dms_data_system RENAME COLUMN path TO dms_path;
ALTER TABLE muk_dms_data_system RENAME COLUMN entry_path TO base_path;

UPDATE muk_dms_data_system SET dms_path = '/' || dms_path || filename;

ALTER TABLE muk_dms_data_system DROP COLUMN filename;

COMMENT ON TABLE muk_dms_data_system IS 'System File Data Model';
COMMENT ON COLUMN muk_dms_data_system.create_uid IS 'Created by';
COMMENT ON COLUMN muk_dms_data_system.dms_path IS 'Document Path';
COMMENT ON COLUMN muk_dms_data_system.checksum IS 'Checksum';
COMMENT ON COLUMN muk_dms_data_system.base_path IS 'Base Path';
COMMENT ON COLUMN muk_dms_data_system.write_uid IS 'Last Updated by';
COMMENT ON COLUMN muk_dms_data_system.write_date IS 'Last Updated on';
COMMENT ON COLUMN muk_dms_data_system.create_date IS 'Created on';