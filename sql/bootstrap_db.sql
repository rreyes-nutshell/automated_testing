-- -- Run this as a superuser (e.g., postgres)

-- DO
-- $$
-- BEGIN
-- 	IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'nsadmin') THEN
-- 		CREATE ROLE nsadmin WITH LOGIN PASSWORD 'nsadmin';
-- 		ALTER ROLE nsadmin CREATEDB;
-- 		RAISE NOTICE 'Role nsadmin created.';
-- 	ELSE
-- 		RAISE NOTICE 'Role nsadmin already exists.';
-- 	END IF;
-- END
-- $$;

-- -- Optionally create a database owned by nsadmin
 DO
 $$
 BEGIN
 	IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ns_ai_tester') THEN
 		CREATE DATABASE ns_ai_tester OWNER nsadmin;
 		RAISE NOTICE 'Database ns_ai_tester created.';
 	ELSE
 		RAISE NOTICE 'Database ns_ai_tester already exists.';
 	END IF;
 END
 $$;
