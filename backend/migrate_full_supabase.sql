-- REGENERACIÓN JERÁRQUICA DE ESQUEMA Y DATOS (V4 FINAL)
SET session_replication_role = 'replica';

DROP TABLE IF EXISTS api_detalleprofesional CASCADE;
DROP TABLE IF EXISTS api_detalleestudiante CASCADE;
DROP TABLE IF EXISTS api_detalledocente CASCADE;
DROP TABLE IF EXISTS api_detallegrupo CASCADE;
DROP TABLE IF EXISTS api_miembrogrupo CASCADE;
DROP TABLE IF EXISTS api_certificado CASCADE;
DROP TABLE IF EXISTS api_inscripcion CASCADE;
DROP TABLE IF EXISTS api_programa_disertantes CASCADE;
DROP TABLE IF EXISTS api_programa CASCADE;
DROP TABLE IF EXISTS api_asistente CASCADE;
DROP TABLE IF EXISTS api_postulaciondisertante CASCADE;
DROP TABLE IF EXISTS api_empresa CASCADE;
DROP TABLE IF EXISTS api_inscripcionprensa CASCADE;
DROP TABLE IF EXISTS api_disertante CASCADE;
DROP TABLE IF EXISTS django_admin_log CASCADE;
DROP TABLE IF EXISTS auth_user_user_permissions CASCADE;
DROP TABLE IF EXISTS auth_user_groups CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS api_edicion CASCADE;
DROP TABLE IF EXISTS auth_user CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;

-- Estructura para django_content_type
CREATE TABLE django_content_type (id integer NOT NULL PRIMARY KEY , app_label VARCHAR(100) NOT NULL, model VARCHAR(100) NOT NULL);

INSERT INTO django_content_type (id, app_label, model) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'permission'),
(3, 'auth', 'group'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session'),
(7, 'api', 'asistente'),
(8, 'api', 'empresa'),
(9, 'api', 'certificado'),
(10, 'api', 'disertante'),
(11, 'api', 'inscripcion'),
(12, 'api', 'miembrogrupo'),
(13, 'api', 'programa'),
(14, 'api', 'configuracioncongreso'),
(15, 'api', 'postulaciondisertante'),
(16, 'api', 'detalleprofesional'),
(17, 'api', 'detalleestudiante'),
(18, 'api', 'detallegrupo'),
(19, 'api', 'edicion'),
(20, 'api', 'detalledocente'),
(21, 'api', 'dashboard'),
(22, 'api', 'inscripcionprensa');

-- Estructura para auth_group
CREATE TABLE auth_group (id integer NOT NULL PRIMARY KEY , name VARCHAR(150) NOT NULL UNIQUE);

-- Estructura para auth_user
CREATE TABLE auth_user (id integer NOT NULL PRIMARY KEY , password VARCHAR(128) NOT NULL, last_login TIMESTAMP NULL, is_superuser BOOLEAN NOT NULL, username VARCHAR(150) NOT NULL UNIQUE, last_name VARCHAR(150) NOT NULL, email VARCHAR(254) NOT NULL, is_staff BOOLEAN NOT NULL, is_active BOOLEAN NOT NULL, date_joined TIMESTAMP NOT NULL, first_name VARCHAR(150) NOT NULL);

INSERT INTO auth_user (id, password, last_login, is_superuser, username, last_name, email, is_staff, is_active, date_joined, first_name) VALUES
(2, 'pbkdf2_sha256$1000000$i4OeCHRA8Kq2k6pWGI6d59$bvgxPjzdsyWmjyMoZhH5FBoKWb75Ufhclf3LHdnzKd8=', '2025-11-19 14:59:33.359116', TRUE, 'lucas', '', 'echavarrialucas1986@gmail.com', TRUE, TRUE, '2025-11-19 14:58:34.418257', ''),
(4, 'pbkdf2_sha256$1000000$DCJ3KqrYniCe3Cwnk6En1U$A9mE9zr/CuChoD1nEyB/DLQEaTxO9ClHI6y08/PWHlc=', '2026-03-10 11:52:12.368770', TRUE, 'congreso', '', 'congresologisticaytransporte@unab.edu.ar', TRUE, TRUE, '2026-03-07 18:05:50.132765', '');

-- Estructura para api_edicion
CREATE TABLE api_edicion (id integer NOT NULL PRIMARY KEY , anio integer NOT NULL UNIQUE, nombre VARCHAR(255) NOT NULL, activa BOOLEAN NOT NULL);

INSERT INTO api_edicion (id, anio, nombre, activa) VALUES
(1, 2025, 'Congreso de Logística 2025', FALSE),
(2, 2026, 'Congreso de Logística 2026', TRUE);

-- Estructura para django_migrations
CREATE TABLE django_migrations (id integer NOT NULL PRIMARY KEY , app VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL, applied TIMESTAMP NOT NULL);

INSERT INTO django_migrations (id, app, name, applied) VALUES
(1, 'contenttypes', '0001_initial', '2025-09-10 13:47:55.357210'),
(2, 'auth', '0001_initial', '2025-09-10 13:47:55.375335'),
(3, 'admin', '0001_initial', '2025-09-10 13:47:55.388745'),
(4, 'admin', '0002_logentry_remove_auto_add', '2025-09-10 13:47:55.403152'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2025-09-10 13:47:55.411837'),
(6, 'api', '0001_initial', '2025-09-10 13:47:55.442899'),
(7, 'contenttypes', '0002_remove_content_type_name', '2025-09-10 13:47:55.460047'),
(8, 'auth', '0002_alter_permission_name_max_length', '2025-09-10 13:47:55.474377'),
(9, 'auth', '0003_alter_user_email_max_length', '2025-09-10 13:47:55.484481'),
(10, 'auth', '0004_alter_user_username_opts', '2025-09-10 13:47:55.493456'),
(11, 'auth', '0005_alter_user_last_login_null', '2025-09-10 13:47:55.503800'),
(12, 'auth', '0006_require_contenttypes_0002', '2025-09-10 13:47:55.507407'),
(13, 'auth', '0007_alter_validators_add_error_messages', '2025-09-10 13:47:55.515092'),
(14, 'auth', '0008_alter_user_username_max_length', '2025-09-10 13:47:55.529937'),
(15, 'auth', '0009_alter_user_last_name_max_length', '2025-09-10 13:47:55.541036'),
(16, 'auth', '0010_alter_group_name_max_length', '2025-09-10 13:47:55.551337'),
(17, 'auth', '0011_update_proxy_permissions', '2025-09-10 13:47:55.562033'),
(18, 'auth', '0012_alter_user_first_name_max_length', '2025-09-10 13:47:55.573169'),
(19, 'sessions', '0001_initial', '2025-09-10 13:47:55.582017'),
(21, 'api', '0002_add_categoria_to_programa', '2025-09-13 13:07:53.107244'),
(22, 'api', '0003_empresa_logo', '2025-09-19 11:53:52.642329'),
(23, 'api', '0004_empresa_cuit_empresa_descripcion_empresa_direccion_and_more', '2025-09-19 11:53:52.661269'),
(24, 'api', '0005_alter_empresa_participacion_opciones', '2025-09-20 10:14:55.155942'),
(25, 'api', '0006_asistente_representante_grupo', '2025-09-20 11:40:34.919056'),
(26, 'api', '0007_alter_disertante_options_alter_programa_categoria', '2025-09-20 14:05:07.072179'),
(27, 'api', '0008_alter_empresa_cargo_contacto_and_more', '2025-09-23 16:27:03.544553'),
(28, 'api', '0009_alter_empresa_options_disertante_linkedin', '2025-09-23 16:43:17.525292'),
(29, 'api', '0010_configuracioncongreso', '2025-09-23 17:54:26.463369'),
(30, 'api', '0011_delete_configuracioncongreso_and_more', '2025-09-24 12:14:53.764258'),
(31, 'api', '0012_alter_asistente_dni', '2025-09-26 00:47:33.835095'),
(32, 'api', '0013_disertante_foto', '2025-09-26 21:58:13.267962'),
(33, 'api', '0014_alter_asistente_profile_type', '2025-09-29 21:03:28.314576'),
(34, 'api', '0015_remove_programa_disertante_programa_disertante_old_and_more', '2025-10-25 23:16:31.811276'),
(35, 'api', '0016_migrate_disertante_to_disertantes', '2025-10-25 23:17:59.758922'),
(36, 'api', '0017_remove_programa_disertante_old', '2025-10-25 23:19:39.046069'),
(37, 'api', '0018_asistente_dni_update_token', '2025-11-11 11:59:21.651964'),
(38, 'api', '0019_asistente_dni_email_sent_and_more', '2025-11-11 11:59:21.676601'),
(39, 'api', '0020_alter_asistente_phone', '2025-11-19 14:56:29.533986'),
(40, 'api', '0021_postulaciondisertante_asistente_terminos_aceptados_and_more', '2026-03-06 23:58:36.454922'),
(41, 'api', '0022_alter_empresa_logo', '2026-03-07 18:47:17.525018'),
(42, 'api', '0023_edicion_alter_inscripcion_asistente_detalledocente_and_more', '2026-03-09 16:30:28.705109'),
(43, 'api', '0024_auto_20260309_1329', '2026-03-09 16:30:28.782266'),
(44, 'api', '0025_remove_asistente_career_and_more', '2026-03-09 16:31:38.710453'),
(45, 'api', '0026_disertante_edicion_disertante_estado_empresa_edicion_and_more', '2026-03-09 17:22:32.122309'),
(46, 'api', '0027_assign_edicion_disertantes_empresas', '2026-03-09 17:22:32.168073'),
(47, 'api', '0028_dashboard_empresa_fecha_registro', '2026-03-11 01:24:26.085630'),
(48, 'api', '0029_add_missing_fields_and_prensa', '2026-03-13 03:20:35.129320');

-- Estructura para django_session
CREATE TABLE django_session (session_key VARCHAR(40) NOT NULL PRIMARY KEY, session_data text NOT NULL, expire_date TIMESTAMP NOT NULL);

INSERT INTO django_session (session_key, session_data, expire_date) VALUES
('bgxh850mul24fngf794puqk5ul8ly7c2', '.eJxVjEEOgjAQRe_StWmm0NLBpXvPQGY6U4saSCisjHdXEha6_e-9_zIDbWsZtqrLMIo5G2dOvxtTeui0A7nTdJttmqd1Gdnuij1otddZ9Hk53L-DQrV8a1THmVuBBEiduAQRQQITRdd59TlqhgbRYySGxgdOKNA7ljaI9GreH_WyOFc:1uwLCR:9H_ZvSKovJDv-ZhRxcjQ4s0z9zkgMYxdtlEmocDHpfg', '2025-09-24 13:49:27.921414'),
('jeesq9z7pgdqucztv4z7xpi5tkwj8z4q', '.eJxVjEEOgjAQRe_StWmm0NLBpXvPQGY6U4saSCisjHdXEha6_e-9_zIDbWsZtqrLMIo5G2dOvxtTeui0A7nTdJttmqd1Gdnuij1otddZ9Hk53L-DQrV8a1THmVuBBEiduAQRQQITRdd59TlqhgbRYySGxgdOKNA7ljaI9GreH_WyOFc:1uwOLP:X7GJsEpHMaLxITqpynNGk-esOjhaD_WMrc6o_Q26ujg', '2025-09-24 17:10:55.010637'),
('jxq9sn34beu8rq74mbev42teoqo4puc1', '.eJxVjEEOgjAQRe_StWmm0NLBpXvPQGY6U4saSCisjHdXEha6_e-9_zIDbWsZtqrLMIo5G2dOvxtTeui0A7nTdJttmqd1Gdnuij1otddZ9Hk53L-DQrV8a1THmVuBBEiduAQRQQITRdd59TlqhgbRYySGxgdOKNA7ljaI9GreH_WyOFc:1uzvoG:Edl4ROC178MZBp1Dku0A68VaQPs3D-qgHKn7q72E11M', '2025-10-04 11:31:20.957294'),
('5a6tgnjt77d4lms2dxjuseb6h3zu5rwo', '.eJxVjEEOgjAQRe_StWmm0NLBpXvPQGY6U4saSCisjHdXEha6_e-9_zIDbWsZtqrLMIo5G2dOvxtTeui0A7nTdJttmqd1Gdnuij1otddZ9Hk53L-DQrV8a1THmVuBBEiduAQRQQITRdd59TlqhgbRYySGxgdOKNA7ljaI9GreH_WyOFc:1v1Nwo:-oVCoBPXGNsE5I8-J1N3-Fo-cb-9E3NUonC7xaGjf-o', '2025-10-08 11:46:10.071582'),
('1waw5ruxafiuu50uafse53f5wq09lvdx', '.eJxVjEEOgjAQRe_StWmm0NLBpXvPQGY6U4saSCisjHdXEha6_e-9_zIDbWsZtqrLMIo5G2dOvxtTeui0A7nTdJttmqd1Gdnuij1otddZ9Hk53L-DQrV8a1THmVuBBEiduAQRQQITRdd59TlqhgbRYySGxgdOKNA7ljaI9GreH_WyOFc:1v3LNt:udVZ3zeDJRff8K0u0V_rjdkz64s3NZJaF4qRTJ2JfJY', '2025-10-13 21:26:13.947895'),
('z3yjhdqjax2dln520atfp3z8j0se81u6', '.eJxVjEEOgjAQRe_StWmm0NLBpXvPQGY6U4saSCisjHdXEha6_e-9_zIDbWsZtqrLMIo5G2dOvxtTeui0A7nTdJttmqd1Gdnuij1otddZ9Hk53L-DQrV8a1THmVuBBEiduAQRQQITRdd59TlqhgbRYySGxgdOKNA7ljaI9GreH_WyOFc:1vIn0A:n5e-JrZ5cr5K054qgyZFgRbjrmmTPmivk4B_c0EKJdI', '2025-11-25 11:57:34.965933'),
('pkkfz7kea1x345i8fjtp2v81sj15qn89', '.eJxVjEEOwiAQRe_C2pAJUAZcuvcMZGBGqRqalHZlvLsh6UK3_7333yrRvtW0d1nTzOqsjDr9bpnKU9oA_KB2X3RZ2rbOWQ9FH7Tr68Lyuhzu30GlXkeNJMaLc7epBDYGIhbBaBHReouMbJxHYusAnKcCQWIWgImCJVuC-nwB0_g3Tg:1vLjef:7iFLzg6YaGkXrT3UUTVAG93cv7tiJrWMOYE9C767i-w', '2025-12-03 14:59:33.385258'),
('183hkatzdxagbqs2kg3iqf2rzqqsox8p', '.eJxVjEEOwiAQRe_C2hAog4BL9z0DGTqMVA0kpV0Z765NutDtf-_9l4i4rSVuPS9xJnERIE6_W8LpkesO6I711uTU6rrMSe6KPGiXY6P8vB7u30HBXr510pkgERNZMMEoCt4xZcsKNEN2ik1KqIczAwfP2oRgHHmLmgdWCsT7AwgnOEA:1vyw2m:TckYXDihFN5vtAezerxuARQPW75RNkxeZWv0UXdPgmA', '2026-03-21 18:06:28.749054'),
('mhr05fpspuhvriux0txfzhzer2c1ty2k', '.eJxVjEEOwiAQRe_C2hAog4BL9z0DGTqMVA0kpV0Z765NutDtf-_9l4i4rSVuPS9xJnERIE6_W8LpkesO6I711uTU6rrMSe6KPGiXY6P8vB7u30HBXr510pkgERNZMMEoCt4xZcsKNEN2ik1KqIczAwfP2oRgHHmLmgdWCsT7AwgnOEA:1vzvdE:lQMrJkbW1C76ib3qOoguwygYg9qAyVJMiGkOsLcb3TA', '2026-03-24 11:52:12.389570');

-- Estructura para auth_permission
CREATE TABLE auth_permission (id integer NOT NULL PRIMARY KEY , content_type_id integer NOT NULL REFERENCES django_content_type (id) DEFERRABLE INITIALLY DEFERRED, codename VARCHAR(100) NOT NULL, name VARCHAR(255) NOT NULL);

INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES
(1, 1, 'add_logentry', 'Can add log entry'),
(2, 1, 'change_logentry', 'Can change log entry'),
(3, 1, 'delete_logentry', 'Can delete log entry'),
(4, 1, 'view_logentry', 'Can view log entry'),
(5, 2, 'add_permission', 'Can add permission'),
(6, 2, 'change_permission', 'Can change permission'),
(7, 2, 'delete_permission', 'Can delete permission'),
(8, 2, 'view_permission', 'Can view permission'),
(9, 3, 'add_group', 'Can add group'),
(10, 3, 'change_group', 'Can change group'),
(11, 3, 'delete_group', 'Can delete group'),
(12, 3, 'view_group', 'Can view group'),
(13, 4, 'add_user', 'Can add user'),
(14, 4, 'change_user', 'Can change user'),
(15, 4, 'delete_user', 'Can delete user'),
(16, 4, 'view_user', 'Can view user'),
(17, 5, 'add_contenttype', 'Can add content type'),
(18, 5, 'change_contenttype', 'Can change content type'),
(19, 5, 'delete_contenttype', 'Can delete content type'),
(20, 5, 'view_contenttype', 'Can view content type'),
(21, 6, 'add_session', 'Can add session'),
(22, 6, 'change_session', 'Can change session'),
(23, 6, 'delete_session', 'Can delete session'),
(24, 6, 'view_session', 'Can view session'),
(25, 7, 'add_asistente', 'Can add asistente'),
(26, 7, 'change_asistente', 'Can change asistente'),
(27, 7, 'delete_asistente', 'Can delete asistente'),
(28, 7, 'view_asistente', 'Can view asistente'),
(29, 8, 'add_empresa', 'Can add empresa'),
(30, 8, 'change_empresa', 'Can change empresa'),
(31, 8, 'delete_empresa', 'Can delete empresa'),
(32, 8, 'view_empresa', 'Can view empresa'),
(33, 9, 'add_certificado', 'Can add certificado'),
(34, 9, 'change_certificado', 'Can change certificado'),
(35, 9, 'delete_certificado', 'Can delete certificado'),
(36, 9, 'view_certificado', 'Can view certificado'),
(37, 10, 'add_disertante', 'Can add disertante'),
(38, 10, 'change_disertante', 'Can change disertante'),
(39, 10, 'delete_disertante', 'Can delete disertante'),
(40, 10, 'view_disertante', 'Can view disertante'),
(41, 11, 'add_inscripcion', 'Can add inscripcion'),
(42, 11, 'change_inscripcion', 'Can change inscripcion'),
(43, 11, 'delete_inscripcion', 'Can delete inscripcion'),
(44, 11, 'view_inscripcion', 'Can view inscripcion'),
(45, 12, 'add_miembrogrupo', 'Can add miembro grupo'),
(46, 12, 'change_miembrogrupo', 'Can change miembro grupo'),
(47, 12, 'delete_miembrogrupo', 'Can delete miembro grupo'),
(48, 12, 'view_miembrogrupo', 'Can view miembro grupo'),
(49, 13, 'add_programa', 'Can add programa'),
(50, 13, 'change_programa', 'Can change programa');
INSERT INTO auth_permission (id, content_type_id, codename, name) VALUES
(51, 13, 'delete_programa', 'Can delete programa'),
(52, 13, 'view_programa', 'Can view programa'),
(53, 14, 'add_configuracioncongreso', 'Can add configuracion congreso'),
(54, 14, 'change_configuracioncongreso', 'Can change configuracion congreso'),
(55, 14, 'delete_configuracioncongreso', 'Can delete configuracion congreso'),
(56, 14, 'view_configuracioncongreso', 'Can view configuracion congreso'),
(57, 15, 'add_postulaciondisertante', 'Can add postulacion disertante'),
(58, 15, 'change_postulaciondisertante', 'Can change postulacion disertante'),
(59, 15, 'delete_postulaciondisertante', 'Can delete postulacion disertante'),
(60, 15, 'view_postulaciondisertante', 'Can view postulacion disertante'),
(61, 16, 'add_detalleprofesional', 'Can add detalle profesional'),
(62, 16, 'change_detalleprofesional', 'Can change detalle profesional'),
(63, 16, 'delete_detalleprofesional', 'Can delete detalle profesional'),
(64, 16, 'view_detalleprofesional', 'Can view detalle profesional'),
(65, 17, 'add_detalleestudiante', 'Can add detalle estudiante'),
(66, 17, 'change_detalleestudiante', 'Can change detalle estudiante'),
(67, 17, 'delete_detalleestudiante', 'Can delete detalle estudiante'),
(68, 17, 'view_detalleestudiante', 'Can view detalle estudiante'),
(69, 18, 'add_detallegrupo', 'Can add detalle grupo'),
(70, 18, 'change_detallegrupo', 'Can change detalle grupo'),
(71, 18, 'delete_detallegrupo', 'Can delete detalle grupo'),
(72, 18, 'view_detallegrupo', 'Can view detalle grupo'),
(73, 19, 'add_edicion', 'Can add edicion'),
(74, 19, 'change_edicion', 'Can change edicion'),
(75, 19, 'delete_edicion', 'Can delete edicion'),
(76, 19, 'view_edicion', 'Can view edicion'),
(77, 20, 'add_detalledocente', 'Can add detalle docente'),
(78, 20, 'change_detalledocente', 'Can change detalle docente'),
(79, 20, 'delete_detalledocente', 'Can delete detalle docente'),
(80, 20, 'view_detalledocente', 'Can view detalle docente'),
(81, 21, 'add_dashboard', 'Can add Dashboard de Estadísticas'),
(82, 21, 'change_dashboard', 'Can change Dashboard de Estadísticas'),
(83, 21, 'delete_dashboard', 'Can delete Dashboard de Estadísticas'),
(84, 21, 'view_dashboard', 'Can view Dashboard de Estadísticas'),
(85, 22, 'add_inscripcionprensa', 'Can add Inscripción Prensa/Influencer'),
(86, 22, 'change_inscripcionprensa', 'Can change Inscripción Prensa/Influencer'),
(87, 22, 'delete_inscripcionprensa', 'Can delete Inscripción Prensa/Influencer'),
(88, 22, 'view_inscripcionprensa', 'Can view Inscripción Prensa/Influencer');

-- Estructura para auth_group_permissions
CREATE TABLE auth_group_permissions (id integer NOT NULL PRIMARY KEY , group_id integer NOT NULL REFERENCES auth_group (id) DEFERRABLE INITIALLY DEFERRED, permission_id integer NOT NULL REFERENCES auth_permission (id) DEFERRABLE INITIALLY DEFERRED);

-- Estructura para auth_user_groups
CREATE TABLE auth_user_groups (id integer NOT NULL PRIMARY KEY , user_id integer NOT NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED, group_id integer NOT NULL REFERENCES auth_group (id) DEFERRABLE INITIALLY DEFERRED);

-- Estructura para auth_user_user_permissions
CREATE TABLE auth_user_user_permissions (id integer NOT NULL PRIMARY KEY , user_id integer NOT NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED, permission_id integer NOT NULL REFERENCES auth_permission (id) DEFERRABLE INITIALLY DEFERRED);

-- Estructura para django_admin_log
CREATE TABLE django_admin_log (id integer NOT NULL PRIMARY KEY , object_id text NULL, object_repr VARCHAR(200) NOT NULL, action_flag smallint  NOT NULL CHECK (action_flag >= 0), change_message text NOT NULL, content_type_id integer NULL REFERENCES django_content_type (id) DEFERRABLE INITIALLY DEFERRED, user_id integer NOT NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED, action_time TIMESTAMP NOT NULL);

INSERT INTO django_admin_log (id, object_id, object_repr, action_flag, change_message, content_type_id, user_id, action_time) VALUES
(179, '65', 'Lucas', 3, '', 8, 4, '2026-03-10 17:18:53.576790'),
(180, '66', 'No', 3, '', 8, 4, '2026-03-10 17:19:59.406158');

-- Estructura para api_disertante
CREATE TABLE api_disertante (id integer NOT NULL PRIMARY KEY , nombre VARCHAR(200) NOT NULL, bio text NOT NULL, foto_url VARCHAR(300) NOT NULL, tema_presentacion VARCHAR(255) NOT NULL, usuario_id integer NULL UNIQUE REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED, linkedin VARCHAR(200) NULL, foto VARCHAR(100) NULL, edicion_id bigint NULL REFERENCES api_edicion (id) DEFERRABLE INITIALLY DEFERRED, estado VARCHAR(20) NOT NULL);

INSERT INTO api_disertante (id, nombre, bio, foto_url, tema_presentacion, usuario_id, linkedin, foto, edicion_id, estado) VALUES
(19, 'Agustin Varamo', 'En un mercado laboral en constante evolución, la empleabilidad se ha convertido en un factor clave para el éxito profesional. Esta charla te brindará las herramientas prácticas y estratégicas para fortalecer tu perfil y destacar en el mundo profesional.', 'ponencias/agustin-varamo.png', 'Empleabilidad', NULL, 'https://www.linkedin.com/in/agustinvaramo', '', 1, 'APROBADO'),
(20, 'Jorge Golfieri', 'Descubrí cómo un simulador ferroviario permite entrenar, planificar y optimizar operaciones ferroviarias, combinando realismo y tecnología avanzada.', 'ponencias/jorge-golfieri.png', 'Simulador ferroviario', NULL, 'https://www.linkedin.com/in/jorge-golfieri-07b638b?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BLoXicdquTmOCLwseaIUPug%3D%3D', NULL, 1, 'APROBADO'),
(21, 'Juan Sanchez', 'Una mirada actual sobre los desafíos y problemáticas que enfrentan los mandos medios en Argentina, explorando sus roles, tensiones y oportunidades de liderazgo.', 'ponencias/juan-sanchez.png', 'Mandos Rotos: Charla actual sobre la problemáticas de los Mandos Medios en Argentina', NULL, 'https://www.linkedin.com/in/jmsanchez-lastmile', NULL, 1, 'APROBADO'),
(22, 'Martin Boris', 'La charla mostrará cómo la tecnología está revolucionando la última milla, permitiendo mayor precisión, trazabilidad y eficiencia en las entregas.', 'ponencias/martin-boris.png', 'Revolucioná tu Logística: Última Milla con Tecnología y Precisión', NULL, 'https://www.linkedin.com/in/boris-martin-15554717a?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BrgRePl1zRrWrA60ddhbGGg%3D%3D', NULL, 1, 'APROBADO'),
(23, 'Gabriel Luchessi', 'Se abordará el papel del marketing como herramienta clave para comunicar y poner en valor la logística dentro de las organizaciones y hacia los clientes.', 'ponencias/gabriel-luchessi.png', 'Marketing: el desafío de explicar la logística', NULL, 'http://linkedin.com/in/gabriellucchesi', NULL, 1, 'APROBADO'),
(24, 'Delfina Salgado', 'Descubrí cómo la Logística 4.0 y la tecnología avanzada están transformando la cadena de suministro, optimizando procesos y potenciando la eficiencia en cada eslabón.', 'ponencias/delfina-salgado.png', 'Logística 4.0: Redefiniendo la Eficiencia en la Cadena de Suministro con Tecnología Avanzada', NULL, 'https://www.linkedin.com/in/delfinalucerosalgado', NULL, 1, 'APROBADO'),
(25, 'Federico Carlos', 'Exploramos los desafíos y oportunidades de la logística portuaria e intermodal, destacando cómo la coordinación entre distintos modos de transporte optimiza la cadena de suministro.', 'ponencias/federico-carlos.png', 'Logística Portuaria e Intermodal.', NULL, 'http://linkedin.com/in/federico-carlos-75a44b80', NULL, 1, 'APROBADO'),
(26, 'Diego Plumaris', 'Analizamos la situación del comercio exterior en Argentina y su interacción con el contexto global, identificando oportunidades, desafíos y tendencias clave para el Comex.', 'ponencias/diego-plumaris.png', 'Comex: Charla sobre la actualidad del comercio exterior en la argentina y en el contexto mundial.', NULL, 'https://www.linkedin.com/in/diego-ariel-plumaris-2967821a', NULL, 1, 'APROBADO'),
(27, 'Cristian Ruiz', 'Explorá cómo la inteligencia artificial, la automatización y los sistemas a medida están transformando la logística, optimizando procesos y redefiniendo la cadena de valor.', 'ponencias/cristian-ruiz.png', 'El Futuro de la Logística: IA, Automatización y Sistemas a Medida', NULL, 'https://www.linkedin.com/in/cristian-facundo-ruiz-diaz-92b766a0?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3Bh0VuzCHfTrijzKLn3TPN4Q%3D%3D', NULL, 1, 'APROBADO'),
(28, 'Natalia Gonzalez', 'La charla propone un recorrido sobre la transformación del rol de los conductores de carga en la Argentina, desde una actividad tradicionalmente vista como un oficio hacia una profesión enmarcada en mayores exigencias técnicas, tecnológicas y de seguridad.', 'ponencias/natalia-gonzalez.png', '"Del oficio a la profesión: La nueva era de los conductores de carga en Argentina"', NULL, 'https://www.linkedin.com/in/natalia-gonzalez-weiber', NULL, 1, 'APROBADO'),
(29, 'Alexander Machado', 'Descubrí cómo Lean Supply Chain 4.0 combina eficiencia sin desperdicio, visibilidad en tiempo real y resiliencia, utilizando tecnología avanzada para optimizar toda la cadena de suministro.', 'ponencias/alexander-machado.png', 'Lean Supply Chain 4.0- Eficiencia sin desperdicio, visibilidad en tiempo real y resiliencia impulsada por la tecnología', NULL, 'https://www.linkedin.com/in/alexander-cardozo-machado-5612b442', NULL, 1, 'APROBADO'),
(30, 'Felipe Rios', 'La charla abordará la evolución del comercio exterior argentino, analizando su recorrido histórico, la situación actual y las perspectivas a futuro en un escenario marcado por la desregulación.', 'ponencias/felipe-rios.png', 'Situación del Comercio Exterior Argentino: Pasado, Presente y Futuro en un Contexto de Desregulación', NULL, 'https://www.linkedin.com/in/felipe-ezequiel-r-84b70b142?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3B%2FOXcg8XMQOmU5S1vz73Crw%3D%3D', NULL, 1, 'APROBADO'),
(31, 'Claudia Freed', 'Se explorará cómo la logística y las cadenas de suministro se están adaptando a los principios de la economía circular, impulsando modelos más sostenibles y eficientes.', 'ponencias/claudia-freed.png', 'Futuro de la logistica/cadenas de suministros y la economia circular.', NULL, 'https://www.linkedin.com/in/claudiafreed', NULL, 1, 'APROBADO'),
(32, 'Ezequiel Grillo', '“Claves para un Transporte Seguro y Competitivo”', 'ponencias/ezequiel-grillo.png', 'Gestión Estratégica de Mercaderías Peligrosas', NULL, 'https://www.linkedin.com/in/ezequielhoraciogrillo', NULL, 1, 'APROBADO'),
(33, 'Ana Gaude', 'Se explorará cómo la incorporación de nuevas tecnologías está transformando los procesos de abastecimiento, optimizando tiempos, reduciendo costos y mejorando la eficiencia en la cadena de suministro.', 'ponencias/ana-gaude.png', 'La incorporacion de tecnologia en el proceso de abastecimiento', NULL, 'https://www.linkedin.com/in/ana-gaude-12a475b', NULL, 1, 'APROBADO'),
(34, 'Jorge Metz', 'Se propone un análisis del momento histórico que atraviesa la Argentina en materia de logística y competitividad.', 'ponencias/jorge-metz.png', 'Puede que estemos viviendo el período más influyente de todos los tiempos en relación a la logística y competitividad en la Argentina', NULL, 'https://www.linkedin.com/in/jorge-metz-714768a7', NULL, 1, 'APROBADO'),
(35, 'Mariano Caiban', 'Analizará los principales retos y oportunidades que enfrenta la entrega al consumidor final, con especial foco en la optimización.', 'ponencias/mariano-caiban.png', 'Desafíos y Oportunidades en la Entrega al Consumidor Final u Optimización de la Última Milla: un Enfoque en la Eficiencia y la Sustentabilidad', NULL, 'https://www.linkedin.com/in/mariano-a-caiban-a943ba233?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BMhEFpNG7QlaGKacvGCD%2BdA%3D%3D', NULL, 1, 'APROBADO'),
(37, 'Arnaldo Ventancu', 'Analizamos la logística minera en Salta, enfocándonos en infraestructura, transporte y cómo potenciar la competitividad internacional del sector.', 'ponencias/arnaldo-ventancu.png', 'La logística minera en Salta: infraestructura, transporte y competitividad internacional', NULL, 'https://www.linkedin.com/in/arnaldo-martin-ventancu-163239176', '', 1, 'APROBADO'),
(39, 'Ignacio Villalon', 'La charla mostrará cómo la tecnología está revolucionando la última milla, permitiendo mayor precisión, trazabilidad y eficiencia en las entregas.', 'ponencias/ignacio-villalon.png', 'Revolucioná tu Logística: Última Milla con Tecnología y Precisión', NULL, 'https://www.linkedin.com/in/ignacio-villalon-351559374?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BZ60t1w1zQ3G655Qa5l5YVw%3D%3D', '', 1, 'APROBADO'),
(41, 'Ernesto Castagnet', 'Analizamos cómo la logística se enfrenta a situaciones de emergencia, tomando como ejemplo las estrategias implementadas en Bahía Blanca para garantizar eficiencia y respuesta rápida.', 'ponencias/ernesto-castagnet.png', 'Logística ante Emergencias: el caso Bahía Blanca', NULL, 'https://www.linkedin.com/in/ernestocastagnet?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BVpper0uFSCi6Fjfm%2Bcwt9A%3D%3D', '', 1, 'APROBADO');

-- Estructura para api_inscripcionprensa
CREATE TABLE api_inscripcionprensa (id integer NOT NULL PRIMARY KEY , nombre_apellido VARCHAR(200) NOT NULL, dni VARCHAR(20) NOT NULL, email VARCHAR(254) NOT NULL, telefono VARCHAR(20) NOT NULL, ciudad_provincia VARCHAR(255) NULL, tipo_perfil VARCHAR(20) NOT NULL, medio_o_canal VARCHAR(255) NOT NULL, url_perfil_red VARCHAR(200) NULL, url_sitio_medio VARCHAR(200) NULL, seguidores_aprox integer NULL, notas_admin text NULL, acepta_tyc BOOLEAN NOT NULL, fecha_inscripcion TIMESTAMP NOT NULL, edicion_id bigint NULL REFERENCES api_edicion (id) DEFERRABLE INITIALLY DEFERRED);

-- Estructura para api_empresa
CREATE TABLE api_empresa (id integer NOT NULL PRIMARY KEY , nombre_empresa VARCHAR(255) NOT NULL, nombre_contacto VARCHAR(255) NULL, email_contacto VARCHAR(254) NULL, celular_contacto VARCHAR(20) NULL, cargo_contacto VARCHAR(255) NULL, participacion_opciones VARCHAR(50) NULL, participacion_otra VARCHAR(255) NULL, logo VARCHAR(100) NULL, cuit VARCHAR(15) NULL, descripcion text NULL, direccion VARCHAR(500) NULL, email_empresa VARCHAR(254) NULL, sitio_web VARCHAR(200) NULL, telefono_empresa VARCHAR(20) NULL, acciones_stand text NULL, acepta_tyc BOOLEAN NOT NULL, computadora_o_pantalla BOOLEAN NOT NULL, estructura_adicional text NULL, gazebo_propio BOOLEAN NOT NULL, participo_edicion_anterior BOOLEAN NOT NULL, requiere_electricidad BOOLEAN NOT NULL, rubro_logistico VARCHAR(255) NULL, tipo_mobiliario VARCHAR(50) NULL, edicion_id bigint NULL REFERENCES api_edicion (id) DEFERRABLE INITIALLY DEFERRED, estado VARCHAR(20) NOT NULL, fecha_registro TIMESTAMP NULL, cantidad_representantes integer NULL, fecha_revision TIMESTAMP NULL, notas_admin text NULL, numero_stand VARCHAR(20) NULL, revisada_por_id integer NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED);

INSERT INTO api_empresa (id, nombre_empresa, nombre_contacto, email_contacto, celular_contacto, cargo_contacto, participacion_opciones, participacion_otra, logo, cuit, descripcion, direccion, email_empresa, sitio_web, telefono_empresa, acciones_stand, acepta_tyc, computadora_o_pantalla, estructura_adicional, gazebo_propio, participo_edicion_anterior, requiere_electricidad, rubro_logistico, tipo_mobiliario, edicion_id, estado, fecha_registro, cantidad_representantes, fecha_revision, notas_admin, numero_stand, revisada_por_id) VALUES
(17, 'Aeronova', 'Contacto Aeronova', 'contacto@aeronova.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/AERONOVA.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(18, 'ARLOG', 'Contacto ARLOG', 'contacto@arlog.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/ARLOG.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(19, 'Cargo', 'Contacto Cargo', 'contacto@cargo.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/LOGO-CARGO.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(20, 'CHAGA', 'Contacto CHAGA', 'contacto@chaga.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/CHAGA.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(21, 'CityOne', 'Contacto CityOne', 'contacto@cityone.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/CITYONE.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(22, 'Conwork', 'Contacto Conwork', 'contacto@conwork.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/CONWORK.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(23, 'EAL Green', 'Contacto EAL Green', 'contacto@ealgreen.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/EAL-GREEN.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(24, 'eTruck', 'Contacto eTruck', 'contacto@etruck.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/ETRUCK.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(25, 'ElectriTruck', 'Contacto ElectriTruck', 'contacto@electritruck.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/ELECTRITRUCK.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(26, 'Escuela de Choferes', 'Contacto Escuela de Choferes', 'contacto@escueladechoferes.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/ESCUELA-CHOFERES.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(27, 'Folkode Group', 'Contacto Folkode Group', 'contacto@folkodegroup.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/Folkode_Group.webp', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(28, 'Genba Kaizen', 'Contacto Genba Kaizen', 'contacto@genbakaizen.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/GENBA-KAIZEN.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(29, 'GLI', 'Contacto GLI', 'contacto@gli.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/GLI.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(30, 'Gruas Golisano', 'Contacto Gruas Golisano', 'contacto@gruasgolisano.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/GRUAS-GOLISANO.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(31, 'ICI', 'Contacto ICI', 'contacto@ici.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/ICI.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(32, 'KMD Logística', 'Contacto KMD Logística', 'contacto@kmdlogística.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/KMD.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(33, 'KPI Consulting', 'Contacto KPI Consulting', 'contacto@kpiconsulting.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/KPI-CONSULTING.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(34, 'La Postal', 'Contacto La Postal', 'contacto@lapostal.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/LA-POSTAL.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(35, 'Logística E-LECE', 'Contacto Logística E-LECE', 'contacto@logísticae-lece.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/ELECE-LOGISTICA.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(36, 'Logística Garpic', 'Contacto Logística Garpic', 'contacto@logísticagarpic.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/LOGISTICA-GARPIC.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(37, 'M-RRHH', 'Contacto M-RRHH', 'contacto@m-rrhh.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/M-RRHH.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(38, 'Muvon', 'Contacto Muvon', 'contacto@muvon.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/MUVON.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(39, 'N&G Transportes', 'Contacto N&G Transportes', 'contacto@n&gtransportes.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/NYG-TRANSPORTES.PNG', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(40, 'Núcleo Logístico', 'Contacto Núcleo Logístico', 'contacto@núcleologístico.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/NUCLEO-LOGISTICO.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(41, 'Performance Lube', 'Contacto Performance Lube', 'contacto@performancelube.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/PERFORMANCE-LUBE.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(42, 'PYB', 'Contacto PYB', 'contacto@pyb.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/PYB.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(43, 'Rasta', 'Contacto Rasta', 'contacto@rasta.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/RASTA.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(44, 'Red Logística', 'Contacto Red Logística', 'contacto@redlogística.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/RED-LOGISTICA.webp', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(45, 'Red Parques Digital', 'Contacto Red Parques Digital', 'contacto@redparquesdigital.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/RED-PARQUES.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(46, 'Shiaffer', 'Contacto Shiaffer', 'contacto@shiaffer.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/SHIAFFER.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(47, 'StarGPS', 'Contacto StarGPS', 'contacto@stargps.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/STARGPS.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(48, 'Surfrigo', 'Contacto Surfrigo', 'contacto@surfrigo.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/SURFRIGO.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(49, 'Traden', 'Contacto Traden', 'contacto@traden.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/TRADEN.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(50, 'Transporte Dominguez', 'Contacto Transporte Dominguez', 'contacto@transportedominguez.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/TRANSPORTE-DOMINGUEZ.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(51, 'UCASAL', 'Contacto UCASAL', 'contacto@ucasal.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/UCASAL.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(52, 'UNLaM', 'Contacto UNLaM', 'contacto@unlam.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/UNLAM.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(53, 'UNLP', 'Contacto UNLP', 'contacto@unlp.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/UNLP.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(54, 'UNLZ', 'Contacto UNLZ', 'contacto@unlz.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/UNLZ.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(55, 'UPE', 'Contacto UPE', 'contacto@upe.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/UPE.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(56, 'UTN', 'Contacto UTN', 'contacto@utn.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/UTN.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(57, 'VDM Logistics', 'Contacto VDM Logistics', 'contacto@vdmlogistics.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/VDM-LOGISTICS.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(58, 'VIMA', 'Contacto VIMA', 'contacto@vima.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/VIMA.png', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(59, 'VOS', 'Contacto VOS', 'contacto@vos.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/VOS.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(60, 'Xperts', 'Contacto Xperts', 'contacto@xperts.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/XPERTS.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(61, 'Zento', 'Contacto Zento', 'contacto@zento.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/Zento.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(62, 'Miniscenics', 'Contacto Miniscenics', 'contacto@miniscenics.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/MINISCENICS.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(63, 'UNS', 'Contacto UNS', 'contacto@uns.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/UNS.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL),
(64, 'Velox', 'Contacto Velox', 'contacto@velox.com', '000000000', 'Representante', 'Sponsor', NULL, 'logos_empresas/VELOX.jpeg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, FALSE, FALSE, NULL, FALSE, FALSE, FALSE, NULL, NULL, 1, 'APROBADO', '2026-03-11 01:24:25.653867', NULL, NULL, NULL, NULL, NULL);

-- Estructura para api_postulaciondisertante
CREATE TABLE api_postulaciondisertante (id integer NOT NULL PRIMARY KEY , nombre_apellido VARCHAR(200) NOT NULL, email VARCHAR(254) NOT NULL, telefono VARCHAR(20) NOT NULL, ciudad_provincia VARCHAR(255) NOT NULL, profesion_cargo VARCHAR(255) NOT NULL, empresa_institucion VARCHAR(255) NOT NULL, linkedin VARCHAR(200) NULL, titulo_charla VARCHAR(255) NOT NULL, ejes_tematicos text NOT NULL , eje_otro text NULL, resumen_charla text NOT NULL, objetivos_charla text NOT NULL, publico_dirigido text NOT NULL , modalidad text NOT NULL , participacion_tipo text NOT NULL , estado VARCHAR(20) NOT NULL, acepta_tyc BOOLEAN NOT NULL, fecha_postulacion TIMESTAMP NOT NULL, edicion_id bigint NULL REFERENCES api_edicion (id) DEFERRABLE INITIALLY DEFERRED, duracion_estimada integer NOT NULL, experiencia_previa text NULL, fecha_revision TIMESTAMP NULL, foto_perfil VARCHAR(100) NULL, notas_admin text NULL, requiere_equipamiento text NULL, revisada_por_id integer NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED, dni VARCHAR(20) NOT NULL);

INSERT INTO api_postulaciondisertante (id, nombre_apellido, email, telefono, ciudad_provincia, profesion_cargo, empresa_institucion, linkedin, titulo_charla, ejes_tematicos, eje_otro, resumen_charla, objetivos_charla, publico_dirigido, modalidad, participacion_tipo, estado, acepta_tyc, fecha_postulacion, edicion_id, duracion_estimada, experiencia_previa, fecha_revision, foto_perfil, notas_admin, requiere_equipamiento, revisada_por_id, dni) VALUES
(1, 'Lucas Echavarria', 'echavarrialucas1986@gmail.com', '1131078008', 'Burzaco', 'Dev', 'No', 'https://www.linkedin.com/in/lucas-echavarria', 'datos en la logística', '["Tecnolog\u00eda e Innovaci\u00f3n en Log\u00edstica"]', '', 'la importancia de la recolección de datos en el proceso logístico', 'dar la explicación de la importancia los objetivos y la toma de decisiones a través de estos', '["Estudiantes", "Acad\u00e9micos/Investigadores", "Profesionales T\u00e9cnicos", "Empresarios/Directivos"]', '["Conferencia individual"]', '["A t\u00edtulo personal"]', 'PENDIENTE', TRUE, '2026-03-07 19:40:29.310432', 1, 30, NULL, NULL, NULL, NULL, NULL, NULL, '32764773'),
(2, 'Lucas Echavarria', 'echavarrialucas1986@gmail.com', '1131078008', 'Burzaco', 'Dev', 'No', 'https://www.linkedin.com/in/lucas-echavarria', 'datos en la logística', '["Tecnolog\u00eda e Innovaci\u00f3n en Log\u00edstica"]', '', 'como tomar decisiones por datos recolectados en la cadena de suministros', 'la importancia de la recolección de datos en la cadena de suministros', '["Empresarios/Directivos", "Profesionales T\u00e9cnicos", "Acad\u00e9micos/Investigadores", "Estudiantes"]', '["Conferencia individual"]', '["A t\u00edtulo personal"]', 'PENDIENTE', TRUE, '2026-03-08 16:52:42.422771', 2, 30, NULL, NULL, NULL, NULL, NULL, NULL, '32764773');

-- Estructura para api_asistente
CREATE TABLE api_asistente (id integer NOT NULL PRIMARY KEY , first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, email VARCHAR(254) NOT NULL UNIQUE, phone VARCHAR(20) NULL, profile_type VARCHAR(30) NOT NULL, asistencia_confirmada BOOLEAN NOT NULL, fecha_confirmacion TIMESTAMP NULL, rol_especifico VARCHAR(255) NULL, dni_update_token VARCHAR(64) NULL UNIQUE, dni_email_sent BOOLEAN NOT NULL, dni_email_sent_date TIMESTAMP NULL, terminos_aceptados BOOLEAN NOT NULL, ciudad_provincia VARCHAR(255) NULL, disertante_vinculado_id bigint NULL REFERENCES api_disertante (id) DEFERRABLE INITIALLY DEFERRED, empresa_vinculada_id bigint NULL REFERENCES api_empresa (id) DEFERRABLE INITIALLY DEFERRED, fecha_registro TIMESTAMP NULL, dni VARCHAR(20) NULL UNIQUE, representante_grupo_id bigint NULL REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED, prensa_vinculada_id bigint NULL REFERENCES api_inscripcionprensa (id) DEFERRABLE INITIALLY DEFERRED);

INSERT INTO api_asistente (id, first_name, last_name, email, phone, profile_type, asistencia_confirmada, fecha_confirmacion, rol_especifico, dni_update_token, dni_email_sent, dni_email_sent_date, terminos_aceptados, ciudad_provincia, disertante_vinculado_id, empresa_vinculada_id, fecha_registro, dni, representante_grupo_id, prensa_vinculada_id) VALUES
(5, 'Brian Agustín', 'Santillán', 'briansantillan1996@gmail.com', '2224524890', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '404579900', NULL, NULL),
(6, 'Sabrina', 'Piersanti', 'Sabripiersanti@hotmail.com', '1136214327', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '395871160', NULL, NULL),
(7, 'Paula Gabriela', 'Acuña', 'palu.gaby.23@gmail.com', '1132711747', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '369304530', NULL, NULL),
(8, 'Camila', 'Vallejos', 'Camii_180397@hotmail.com', '1137774690', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(9, 'Alexander Agustín', 'Farias', 'fariasalexander1999@gmail.com', '1162230257', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '420142590', NULL, NULL),
(10, 'Tania', 'Cabana', 'tary87_04@hotmail.com', '‪+54 9 11 6835‑9653‬', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(11, 'Fernando', 'Scarella', 'fernandoscarella93@gmail.com', '1551758365', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '376820540', NULL, NULL),
(12, 'Melany Brisa', 'Llane', 'Melanybrisallane@gmail.com', '1157245788', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '426214710', NULL, NULL),
(13, 'ayelén', 'Cuevas', 'Ayesantibrian@gmail.com', '2224-535111', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '381543320', NULL, NULL),
(14, 'Nelson', 'Soria', 'dario.snd@gmail.com', '1133557370', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '353801040', NULL, NULL),
(15, 'Oriana jael', 'carminati', 'carminatioriana@gmail.com', '1149358960', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(16, 'Walter', 'taboada', 'Walterlogistica@hotmail.com', '2224498156', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(17, 'Juan manuel', 'pereyra', 'Juanma-71@hotmail.com', '1123086241', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '378422260', NULL, NULL),
(18, 'Cristian', 'Gómez', 'eduanaambar@gmail.com', '1130394529', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '327552360', NULL, NULL),
(19, 'Lucas Agustín', 'Tur', 'turlucasagustin85@gmail.com', '1130248444', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(20, 'Adrian Elias', 'Umpierrez', 'umpierrezadrianunab@gmail.com', '1157994372', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(21, 'Gabriel', 'Diaz', 'Gabydiaztiesto@gmail.com', '1124831584', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '399798070', NULL, NULL),
(22, 'Brian Ezequiel', 'Serrano', 'Serranobrian22@gmail.com', '1158965769', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '379963400', NULL, NULL),
(23, 'Cristian Fabián', 'Cardozo', 'cardozofabian29@gmail.com', '1123961785', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '310898500', NULL, NULL),
(24, 'Germán', 'Godoy', 'Gerthiagodoy@gmail.com', '1160399105', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(25, 'Ana Luz', 'Artaza', 'luzaniita@gmail.com', '1154013964', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '472012270', NULL, NULL),
(26, 'Miguel', 'Passero', 'miguelpassero1982@hotmail.com', '1133481387', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '299112450', NULL, NULL),
(27, 'Gabriel', 'Noguera', 'Gabrielnoguera1983@gmail.com', '1163350610', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '300466300', NULL, NULL),
(28, 'Segovia', 'Ramón', 'arisego24@gmail.com', '1135008009', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '288339220', NULL, NULL),
(29, 'Yesica', 'Gonzalez', 'yesicagonzalez.c90@gmail.com', '1139179754', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '359933170', NULL, NULL),
(30, 'Roxana', 'Sosa', 'roxanaso79@hotmail.com', '1135142142', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(31, 'Gonzalo ezequiel', 'sanchez negrete', 'Gonzalomancu92@gmail.com', '1163649003', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(32, 'Gustavo Adrian', 'González', 'Gusgonzalez1971@gmail.com', '1165259036', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '220005870', NULL, NULL),
(33, 'Saul Osmar', 'Tourn', 'saul.osmar.tourn@gmail.com', '1132613462', 'STUDENT', FALSE, NULL, 'Colaborador Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '389345220', NULL, NULL),
(34, 'Lucas Emmanuel', 'Ledesma', 'Lucas.ledesma2406@gmail.com', '1144118257', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '445137930', NULL, NULL),
(35, 'Mariana', 'ojeda', 'Marianojeda534@gmail.com', '1158703823', 'STUDENT', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(36, 'Yonathan Ezequiel', 'Gomez', 'yonatahnp.gomez@gmail.com', '1149354322', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '342626210', NULL, NULL),
(37, 'Roxana', 'Insaurralde', 'Roxanainsaurralde65@gmail.com', '1150502578', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(38, 'Macarena', 'San Millán', 'Msanmillan95@gmail.com', '1556055003', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '388874730', NULL, NULL),
(39, 'Jimena soledad', 'Molina', 'Jimemeji56@gmail.com', '1161707293', 'STUDENT', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '343032990', NULL, NULL),
(40, 'Claudio Ezequiel', 'Avendaño', 'Claudio2656@gmail.com', '1165188979', 'STUDENT', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '333384630', NULL, NULL),
(41, 'Jonathan  Alberto', 'Varela', 'Jonathanvarela_@outlook.es', '1157263145', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '388239990', NULL, NULL),
(42, 'Nerea Agostina', 'Orellana', 'nerea.orellana.dml@gmail.com', '1125165172', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(43, 'juan segundo', 'silaui', 'jsegundosilaui@gmail.com', '1135706354', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(44, 'Gustavo Raul', 'Echegaray', 'gustavo-echegaray@hotmail.com', '1164584724', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(45, 'Noelia', 'Kairuz', 'noelia.kairuz@diagroup.com', '1168705970', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(46, 'Agustin', 'Cavalli', 'agustincavalli.ac@gmail.com', '1125077829', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '409039000', NULL, NULL),
(47, 'Guido', 'Martinelli', 'guidofmartinelli@gmail.com', '1160240315', 'TEACHER', FALSE, NULL, 'Colaborador/a Docente', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(48, 'Sol Micaela', 'Amaya', 'solcitoamaya.sa@gmail.com', '1133481924', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(49, 'Jonatan', 'Lionel', 'jonatanlioneldacruz@gmail.com', '1132842781', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '323585910', NULL, NULL),
(50, 'Cecilia', 'Pérez Pereyra', 'ceciriel.p@gmail.com', '1150405776', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(51, 'Jorge David', 'Gonzalez', 'fotoenfocodavid@gmail.com', '1133515426', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '304474240', NULL, NULL),
(52, 'Walter Daniel', 'Del Castillo', 'danyhet84@gmail.com', '1134062459', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '371936430', NULL, NULL),
(53, 'Fernando Ariel', 'Lavega', 'fernandolavega@gmail.com', '1128376450', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '272797420', NULL, NULL),
(54, 'Alejo Ezequiel', 'Velazquez Ramos', 'alejovelazquezramos@gmail.com', '541135837326', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL);
INSERT INTO api_asistente (id, first_name, last_name, email, phone, profile_type, asistencia_confirmada, fecha_confirmacion, rol_especifico, dni_update_token, dni_email_sent, dni_email_sent_date, terminos_aceptados, ciudad_provincia, disertante_vinculado_id, empresa_vinculada_id, fecha_registro, dni, representante_grupo_id, prensa_vinculada_id) VALUES
(55, 'Aldana', 'Flores', 'flores.aldana2003@gmail.com', '1136371204', 'GRADUADO', FALSE, NULL, 'Colaborador/a Graduado', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(56, 'Cristian', 'Crivelli', 'Cristiancrivelli@gmail.com', '1137677745', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '292471890', NULL, NULL),
(57, 'Carlos Alberto', 'Vázquez', 'Cvazquezcargo@gmail.com', '1133738230', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(58, 'Fiorella Denisse', 'Lepore', 'fiorellalepore281@gmail.com', '1169312455', 'STUDENT', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '421486580', NULL, NULL),
(59, 'Mariano', 'Ponce de Leon', 'poncedeleonma@gmail.com', '1130843526', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '265426790', NULL, NULL),
(60, 'Gaston Lucas', 'oyola', 'gastonlucasoyola@gmail.com', '1137550962', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '345305770', NULL, NULL),
(61, 'Adrián Osvaldo', 'Alvarez', 'adrianosvaldoalvarez@gmail.com', '+5492616091537', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(62, 'Florencia Anabel', 'Lo Votrico', 'florencialovotrico@gmail.com', '+541123517002', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '447099240', NULL, NULL),
(63, 'Leila Marina', 'Aliberti', 'laliberti1@abc.gob.ar', '01130787738', 'STUDENT', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(64, 'Leonardo Javier', 'Vargas', 'leonardovargas2230@gmail.com', '1166696253', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '350716880', NULL, NULL),
(65, 'Thomas Alejo Domingo', 'Travieso Rivero', 'alejorivero62@gmail.com', '01169022851', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '400064550', NULL, NULL),
(66, 'Alejandro', 'Plançon', 'alejandro.plancon@gmail.com', '1128551582', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(67, 'Georgina Paola', 'Boetti Ortega', 'Pao_2505boetti@hotmail.com', '01138795205', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(68, 'Julio Ricardo', 'Busteros', 'busterosjulio4@gmail.com', '1158179015', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(69, 'Nelida', 'Albornoz', 'Albornoznel@gmail.com', '1139260785', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(70, 'Xiomara Magali', 'Bravo', 'magalibravo016@gmail.com', '01157435972', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(71, 'Milagros', 'Nieto', 'milinieto7@gmail.com', '1145397420', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '452998880', NULL, NULL),
(72, 'Laura Carolina', 'Lucero Limachi Paredes', 'llimachiparedes.1@gmail.com', '01150241089', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '406745230', NULL, NULL),
(73, 'Clader David', 'Ruiz Riveros', 'Cdavidruiz88@gmail.com', '1127441129', 'STUDENT', FALSE, NULL, 'Colaborador/a Estudiante', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(74, 'Federico Maximiliano', 'Rojas Gonzalez', 'federicoxeneize90@gmail.com', '1157634282', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(75, 'Nicolás Omar', 'corso', 'Nicolasomarcorso@outlook.es', '1126848681', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '379335060', NULL, NULL),
(76, 'Sergio Gabriel', 'Benítez', 'Sergiobenitez.correo@gmail.com', '1121871771', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(77, 'Rodrigo Nahuel', 'Chaile', 'Rodrigonahuelchaile1@gmail.com', '01138031597', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '438770810', NULL, NULL),
(78, 'Laura carolina', 'Laz', 'Lazlaura63@gmail.com', '1128539035', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '354972890', NULL, NULL),
(79, 'Andres', 'Diaz', 'andres.diaz041190@gmail.com', '541128804218', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '218872060', NULL, NULL),
(80, 'Cintia', 'Olguin', 'nucleologistico.ar@gmail.com', '2657244137', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '308397420', NULL, NULL),
(81, 'agustina', 'iglesias', 'agussiglesias9@gmail.com', '01144080111', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '437826710', NULL, NULL),
(82, 'Eugenia Abril', 'Medina', 'Mgulf2504@gmail.com', '2224529395', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(83, 'Belen Ariadna', 'Ramos', 'b.ariadna.r@gmail.com', '1165729268', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(84, 'VICTOR ISRAEL', 'GARCÍA SÁNCHEZ', 'victorgarcia@chainsolutions.mx', '+526643070130', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(85, 'Sebastian', 'consoli', 'sebastianconsoli72@gmail.com', '1121553537', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '328497880', NULL, NULL),
(86, 'Milagros antonella', 'sandoval', 'Milagrossandoval80697@gmail.com', '1171354484', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '500140080', NULL, NULL),
(87, 'Sergio Gustavo', 'Abregu', 'sgasalsero@gmail.com', '1132126744', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '303712680', NULL, NULL),
(88, 'Federico Mario', 'Boga', 'pipefede@gmail.com', '01131664774', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '273087880', NULL, NULL),
(89, 'Cintia Analía', 'Rios', 'Cyana2005@hotmail.com', '1138957132', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '295421820', NULL, NULL),
(90, 'Mauro Nahuel', 'Mansilla', 'mauronahuelmansilla@gmail.com', '0111535253790', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '351892210', NULL, NULL),
(91, 'Camila', 'Bonaldi', 'Bonaldica@gmail.com', '01133151113', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '422266130', NULL, NULL),
(92, 'Camila Belén', 'Burgos', 'camiiburgos80@gmail.com', '1162067676', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '428725160', NULL, NULL),
(93, 'Jorge', 'Esquivel', 'esquivel1181@yahoo.com.ar', '1151355908', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '264950790', NULL, NULL),
(94, 'Micaela belen', 'nuñez', 'Miika.belen1502@gmail.com', '1135037807', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '365563920', NULL, NULL),
(95, 'Luis alejandro', 'godoy', 'Luisalejandrogodoy02@gmail.com', '1162936210', 'OTRO', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '309748190', NULL, NULL),
(96, 'Brenda', 'González', 'saragonzalezb959@gmail.com', '1138969452', 'TEACHER', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '386319380', NULL, NULL),
(97, 'Cesar Andrés', 'Bejarano', 'cesarbe878@gmail.com', '1141415795', 'VISITOR', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '379865850', NULL, NULL),
(98, 'Alonso', 'gonzalo', 'Gonzalo.alonso@importadoranch.com', '1167981167', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '317212890', NULL, NULL),
(99, 'Stella Maris itati', 'Monzón', 'stellamarislu@gmail.com', '1123089038', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '319891190', NULL, NULL),
(100, 'Agostina', 'Galichio', 'agosgalic@gmail.com', '1162172232', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '4627612370', NULL, NULL),
(101, 'Olga', 'Vazquez', 'Olga.bvazquez@gmail.com', '1154681779', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '273123510', NULL, NULL),
(102, 'Bella sol', 'Fabiani', 'bellasolfabiani0@gmail.com', '01168921718', 'VISITOR', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '445444080', NULL, NULL),
(103, 'Tamara Ayelen', 'Orellana', 'Tam.orellana1503@gmail.com', '1127381203', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '430859890', NULL, NULL),
(104, 'Elias ezequiel', 'Rodriguez', 'rodriguezeliasezequiel017@gmail.com', '1144138841', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '442850050', NULL, NULL);
INSERT INTO api_asistente (id, first_name, last_name, email, phone, profile_type, asistencia_confirmada, fecha_confirmacion, rol_especifico, dni_update_token, dni_email_sent, dni_email_sent_date, terminos_aceptados, ciudad_provincia, disertante_vinculado_id, empresa_vinculada_id, fecha_registro, dni, representante_grupo_id, prensa_vinculada_id) VALUES
(105, 'Ian', 'Morilla', 'ianmorilla8@gmail.com', '1173637588', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '422917660', NULL, NULL),
(106, 'Sofia', 'Jacamo', 'Jacamo.sofiaa@gmail.com', '1135909121', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '445207820', NULL, NULL),
(107, 'Lionel', 'Mendoza', 'mendozagerardolionel@gmail.com', '1126325774', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '315313580', NULL, NULL),
(108, 'Diego', 'Acosta', 'Acosta_diegoezequiel@hotmail.com', '1134953327', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '341230530', NULL, NULL),
(109, 'Kevin Samuel', 'Alegre', 'samuelalegre1665@gmail.com', '1125978677', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '374225380', NULL, NULL),
(110, 'Mariano Victor', 'Marlier', 'marlier1980@gmail.com', '1162543228', 'GRADUADO', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '280436700', NULL, NULL),
(111, 'Kevin Alejandro', 'Alais', 'Kevin27_alais@hotmail.com', '1141938791', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '368196790', NULL, NULL),
(112, 'Silvana Eugenia', 'Abalsamo', 'madonica2089@gmail.com', '1131501312', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '342729450', NULL, NULL),
(113, 'Sofia Camila', 'Ochoa', 'sofiaperez64@gmail.com', '1165250223', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '464289810', NULL, NULL),
(114, 'Marcelo', 'Catania', 'majacat2008@gmail.com', '01169614971', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '268943400', NULL, NULL),
(115, 'Lucila Milagro', 'Palmuchi', 'lpalmuchi@gmail.com', '+5491127692518', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '466378190', NULL, NULL),
(116, 'Camila Rocio', 'Montiel', 'Cammilamontiel28@gmail.com', '01125382773', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '412113480', NULL, NULL),
(117, 'María Alejandra', 'Schell', 'Schellalejandra2016@gmail.com', '34243003', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(118, 'Juan Pablo', 'Bernardez', 'juanbernardez88@gmail.com', '1150067743', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '339140050', NULL, NULL),
(119, 'Santiago Martín', 'Acosta', 'santi.m.acosta@hotmail.com', '1133596819', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '409233640', NULL, NULL),
(120, 'Marcelo Alejandro', 'Esposito', 'mespo126@gmail.com', '1166528601', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '211230980', NULL, NULL),
(121, 'Jaqueline Daniela', 'Acevedo', 'jaquelineacev@gmail.com', '01153224594', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '369443720', NULL, NULL),
(122, 'Marcelo', 'Mascarini', 'usa@esperandovia.com', '1167649994', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '323442750', NULL, NULL),
(123, 'Pablo César', 'Jacquet', 'pcjacquet79@gmail.com', '1165298511', 'PROFESSIONAL', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '276301170', NULL, NULL),
(124, 'Verónica elizabeth', 'Vallejos', 'zarachoelizabeth0@gmail.com', '2213646935', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '444264250', NULL, NULL),
(125, 'Natalia', 'Salazar', 'Nsalazar@correoargentino.com.ar', '1165641981', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '321883920', NULL, NULL),
(126, 'Ortiz', 'Graciela', 'g.ortiz@kmd-logistica.com.ar', '1123775712', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '291928740', NULL, NULL),
(127, 'Luciano Rodrigo', 'Tapia', 'lucianorodrigotapia@gmail.com', '1167048538', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '386353450', NULL, NULL),
(128, 'Lorena', 'Morante', 'Lorena.morante@elsalvador.com.ar', '2914740388', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '251345980', NULL, NULL),
(129, 'Emilio Hugo', 'Romero', 'emiliohugoromero@gmail.com', '1133649624', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '369162920', NULL, NULL),
(130, 'Magali', 'Montoya', 'mmontoya860@alumnos.iua.edu.ar', '3516879187', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(131, 'Roberto Ariel', 'Gomez', 'ag7867870@gmail.com', '1136480293', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '284976500', NULL, NULL),
(132, 'Micaela Belén', 'Panto', 'micapanto21@gmail.com', '1138796458', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '443791250', NULL, NULL),
(133, 'Juan Pablo', 'Palacios', 'Juanpablopalacios57@gmail.com', '1140483258', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '330382410', NULL, NULL),
(134, 'MATÍAS NAHUEL', 'GALLARDO', 'matiasbng19@gmail.com', '1136987506', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '449675520', NULL, NULL),
(135, 'Maximiliano Martín', 'Maza', 'maximilianomaza91@gmail.com', '1148329296', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '367848680', NULL, NULL),
(136, 'Pamela Roxana', 'Rua', 'mamacora777@gmail.com', '1156201945', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '284233460', NULL, NULL),
(137, 'Vanesa Judith', 'González', 'vanegon1274@gmail.com', '1176409377', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '410061210', NULL, NULL),
(138, 'Flavia Elisa', 'Gómez', 'flaviaegomez@gmail.com', '1161468445', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '278157630', NULL, NULL),
(139, 'Diego Jesús', 'Velardez', 'velardezdiego1981@gmail.com', '+5491127195777', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '288922150', NULL, NULL),
(140, 'Hernan', 'Garreta', 'hgarret14@gmail.com', '1140411584', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '234177360', NULL, NULL),
(141, 'Hugo Eliseo', 'Fazio', 'hfazio17@gmail.com', '1167927036', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '177985310', NULL, NULL),
(142, 'Pablo Agustín', 'Rutti', 'rutti38@gmail.com', '01125213235', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '381478200', NULL, NULL),
(143, 'Julián', 'Napoli', 'juliannapoli.madero@hotmail.com', '+5491122500960', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '418234530', NULL, NULL),
(144, 'Ana', 'Gambirassi', 'gambirassi.ana@gmail.com', '1167952932', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '416468950', NULL, NULL),
(145, 'Alejandra Gimena', 'Reyss Globsky', 'Alereyes12345678910@gmail.com', '1153864930', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '939496310', NULL, NULL),
(146, 'Rodrigo Quimey', 'Ponce de León', 'Rodrigoquimey@gmail.com', '1165898653', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '407605020', NULL, NULL),
(147, 'Mariela', 'calegari', 'calegarimsc@gmail.com', '1156057258', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '341425430', NULL, NULL),
(148, 'Alicia', 'Britez', 'aliciabritez0702@gmail.com', '1128596793', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '283629970', NULL, NULL),
(149, 'Franco Gabriel', 'Del Castillo', 'francogabrieldelcastillo@gmail.com', '1156936951', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '391847890', NULL, NULL),
(150, 'Nadia marisa', 'zorreguieta Segura', 'nadiazs@hotmail.com', '1141743254', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '290066180', NULL, NULL),
(151, 'Carla', 'Coste', 'karcoste@gmail.com', '1553888834', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '326858530', NULL, NULL),
(152, 'Ernesto', 'Pereira', 'info@transportespereira.com.ar', '111', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '235227630', NULL, NULL),
(153, 'Karen Eliana', 'Ayala', 'eliayala260@gmail.com', '2213032818', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '379796250', NULL, NULL),
(154, 'Héctor', 'Toledo', 'Htoledo@andromaco.com.ar', '1127141238', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '234679120', NULL, NULL);
INSERT INTO api_asistente (id, first_name, last_name, email, phone, profile_type, asistencia_confirmada, fecha_confirmacion, rol_especifico, dni_update_token, dni_email_sent, dni_email_sent_date, terminos_aceptados, ciudad_provincia, disertante_vinculado_id, empresa_vinculada_id, fecha_registro, dni, representante_grupo_id, prensa_vinculada_id) VALUES
(155, 'Jesica Gisela', 'Heredia', 'Jesica214heredia@gmail.com', '1141817601', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '319675350', NULL, NULL),
(156, 'Leandro Ezequiel', 'Agesta', 'Agestaleandro338@gmail.com', '1158628208', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '368203250', NULL, NULL),
(157, 'Brian Gabriel', 'Arias', 'Ariasbriang@gmail.com', '1121920514', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '407608590', NULL, NULL),
(158, 'Micaela', 'Mazzaro', 'Mazzaromica@gmail.com', '1166612519', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '395626860', NULL, NULL),
(159, 'Nicolás', 'Cardozo', 'cardozo.nicolas9491@gmail.com', '1134504393', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '382003360', NULL, NULL),
(160, 'Fabio Ariel', 'Cerracchio', 'cerracchiofabio@gmail.com', '1140475073', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '273870460', NULL, NULL),
(161, 'María Laura', 'Nicolau', 'licenciadacomex@hotmail.com', '2215667889', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '240950550', NULL, NULL),
(162, 'Yamila Alejandra', 'Garcia', 'garcia62115@estudiantes.untref.edu.ar', '1132345229', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '302830370', NULL, NULL),
(163, 'Facundo', 'Gasparotti', 'facugasparotti01@gmail.com', '01126530190', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '433165000', NULL, NULL),
(164, 'Jose', 'Monteagudo', 'josemonteagudolog@gmail.com', '1123585467', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '353470780', NULL, NULL),
(165, 'Sacha', 'Paez Gigena', 'sachapaezgigena@gmail.com', '1167993100', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '394322460', NULL, NULL),
(166, 'Federico Ezequiel', 'Matteucci', 'federicoematteucci@gmail.com', '1160109537', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '470689220', NULL, NULL),
(167, 'Lucas Andrés', 'Pérez Diaz', 'lxcaspd@gmail.com', '1134091915', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '477535510', NULL, NULL),
(168, 'Matías Nicolás', 'Márquez Anadón', 'mmarquezanadon@gmail.com', '1165679145', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '342304900', NULL, NULL),
(169, 'Rodrigo Andres', 'Sanchez Marinkovic', 'rsanchez@fecoset.org.ar', '1136402408', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '952894240', NULL, NULL),
(170, 'Karen', 'larrue', 'Karenlarrue13@gmail.com', '01166830893', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '381512030', NULL, NULL),
(171, 'Alejandro Emanuel', 'Perez Yupanqui', 'perezalejandroetn5@gmail.com', '1153469209', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '393883480', NULL, NULL),
(172, 'Martín Ezequiel', 'Morales Kanerva', 'martinmoralesk@gmail.com', '1155624403', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '306032320', NULL, NULL),
(173, 'Higo', 'Gallo', 'hsgallo@hotmail.com', '0111541626090', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '239520980', NULL, NULL),
(174, 'Duilio Néstor Luis', 'Capasso', 'luiscapasso77@gmail.com', '1140991009', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '144004160', NULL, NULL),
(175, 'Kiara', 'Sosa Stieben', 'Sosastiebenk@gmail.com', '2224511750', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '472161790', NULL, NULL),
(176, 'Iglesias', 'Estefania', 'iglesiasestefania17@gmail.com', '01156064081', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '431007130', NULL, NULL),
(177, 'Esteban Facundo', 'Aguirre', 'estebanfacundoag@gmail.com', '0111553112427', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '266795610', NULL, NULL),
(178, 'Luciano Martin', 'Juárez', 'juarez48443@estudiantes.untref.edu.ar', '1163583281', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '290683030', NULL, NULL),
(179, 'Leonardo', 'Chazarreta', 'leonardo.chazarreta@enaex.com', '1135802629', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '248208940', NULL, NULL),
(180, 'Tomas Agustín', 'marino', 'Tomas.marino.03@gmail.com', '0116784417', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '451739340', NULL, NULL),
(181, 'Cristian', 'Flores', 'Cruzrojo18@gmail.com', '1136395276', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '337144190', NULL, NULL),
(182, 'Emilio Nicolás', 'Rocha', 'rochaemilionicolas@gmail.com', '01122736672', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '442057890', NULL, NULL),
(183, 'Nicolás Javier', 'Amador', 'Nicolasamador2014@outlook.com', '1127639234', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '412632030', NULL, NULL),
(184, 'Sabrina Elisabet', 'Godoy', 'godoysabrinaelisabet@gmail.com', '01123554040', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '326612390', NULL, NULL),
(185, 'Alejandro', 'Garcia Loně', 'alegarcialone@gmail.com', '1141619117', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '932868430', NULL, NULL),
(186, 'Leandro', 'maidana', 'leanmaidana27@gmail.com', '1173612460', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '420290850', NULL, NULL),
(187, 'Sofia Ariadna', 'isla', 'sofiaariadna0404@gmail.com', '0111559536606', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '457352650', NULL, NULL),
(188, 'Pamela yamila', 'Lara', 'yamilachaile9@gmail.com', '1126784370', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '323436760', NULL, NULL),
(189, 'Jesica Daniela', 'Henriques', 'henriquesjesica@gmail.com', '1155786282', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '391178570', NULL, NULL),
(190, 'Lorena Gisele', 'Romero', 'lohromero25@gmail.com', '1138129287', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '388530150', NULL, NULL),
(191, 'Olivia', 'Damaris Yllodo', 'oliviayllodo97@gmail.com', '541130362292', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '470183530', NULL, NULL),
(192, 'Jessica Noemi', 'Ramirez', 'jessicanoemiramirez57@gmail.com', '1130549374', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '369468640', NULL, NULL),
(193, 'MIRNA', 'ZANNINI', 'ZANNINIMIRNA@GMAIL.COM', '1559988789', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '352277120', NULL, NULL),
(194, 'Ezequiel Darío', 'Vargas', 'ezedarvar17@gmail.com', '1124834721', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '415639870', NULL, NULL),
(195, 'Valentina', 'alvarez', 'Valentinaalem2000@gmail.com', '02224463614', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '470920110', NULL, NULL),
(196, 'Cintia Elisabet', 'Iglesias', 'iglesias.cintiaelisabet@gmail.com', '1124019640', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '333008870', NULL, NULL),
(197, 'Gabriela elizabeth', 'palavecino', 'gabrielapalavecino@hotmail.com', '1139336011', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '261179450', NULL, NULL),
(198, 'Vivian Elena', 'Centeno', 'vec2015eve@gmail.com', '1124546415', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '203483080', NULL, NULL),
(199, 'Tatiana Belén', 'Vera', 'tatiana.belen.vera@gmail.com', '0111566685684', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '339510740', NULL, NULL),
(200, 'Talia Pamela', 'Salazar', 'salazar96talia@gmail.com', '01159267560', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '429600550', NULL, NULL),
(201, 'Martín Germán', 'Scalone', 'martinscalone@gmail.com', '1151062652', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '306110500', NULL, NULL),
(202, 'casandra carolina', 'lazarte', 'Casandracarolinalazarte@gmail.com', '1157176903', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '425704500', NULL, NULL),
(203, 'Matías', 'Montivero', 'matias.montivero@hotmail.com', '1164380418', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '399192440', NULL, NULL),
(204, 'Alondra Lucila Luna', 'Erneta', 'alolunaerneta@gmail.com', '91126764769', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '469878400', NULL, NULL);
INSERT INTO api_asistente (id, first_name, last_name, email, phone, profile_type, asistencia_confirmada, fecha_confirmacion, rol_especifico, dni_update_token, dni_email_sent, dni_email_sent_date, terminos_aceptados, ciudad_provincia, disertante_vinculado_id, empresa_vinculada_id, fecha_registro, dni, representante_grupo_id, prensa_vinculada_id) VALUES
(205, 'Romina', 'Beatriz', 'trocheromina55@gmail.com', '+541168867881', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '958167760', NULL, NULL),
(206, 'Alejo Nicolas', 'Barbot', 'Alejo.unab25@outlook.com.ar', '01123871263', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '418010490', NULL, NULL),
(207, 'Ana Isabel', 'Suarez', 'anasuareznazareno@gmail.com', '1169377375', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '232921320', NULL, NULL),
(208, 'Maximiliano', 'ledesma', 'kingdoomfrozen@gmail.com', '1135822321', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '353461370', NULL, NULL),
(209, 'Rosa Esther', 'Palmuchi', 'palmuchi.r.76@gmail.com', '1136610507', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '256013370', NULL, NULL),
(210, 'Margarita Elena', 'Nuñez', 'nunezmargaritaelena@gmail.com', '1130753360', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '226567860', NULL, NULL),
(211, 'Santiago Ramón', 'Rolón', 'sant10_sr@hotmail.com', '1126516083', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '327646810', NULL, NULL),
(212, 'Virginia Elizabeth', 'Morinigo', 'morinigovirginia@gmail.com', '01127689627', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '388354630', NULL, NULL),
(213, 'Fernando', 'Groba', 'fergrb.ux@gmail.com', '1153370291', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '313771250', NULL, NULL),
(214, 'Sabrina Soledad', 'Cáceres', 'sabrinacaceres431@gmail.com', '1130131828', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '285930610', NULL, NULL),
(215, 'Claudio', 'Gonzalez', 'claudio.gonzalez@docentes.unab.edu.ar', '1163606811', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '219964760', NULL, NULL),
(216, 'raquel', 'dina', 'dinalizarraga@gmail.com', '1157680936', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '188820280', NULL, NULL),
(217, 'Celina Luna', 'Marina', 'marinalunaa01@gmail.com', '1134315766', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '439149130', NULL, NULL),
(218, 'Natalia Noemí', 'Indalecio', 'nataliaindalecio@gmail.com', '1159582298', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '240640830', NULL, NULL),
(219, 'Sabrina Amira', 'Ametoski Dorneles', 'aametoski@gmail.com', '01164553341', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '383976490', NULL, NULL),
(220, 'Nestor Ivan', 'Michel', 'Michelnestorivan@gmail.com', '1169741507', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '362857990', NULL, NULL),
(221, 'Camila Macarena', 'Solari', 'camilasolari3@gmail.com', '1125365890', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '433889230', NULL, NULL),
(222, 'Hernan Hector', 'Quintana', 'hernanquintana221@gmail.com', '1124050746', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '330862210', NULL, NULL),
(223, 'Florencia Giselle', 'Villordo', 'florenciagisellev@gmail.com', '1166903818', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '446088510', NULL, NULL),
(224, 'Mayra Nicole', 'Perez', 'Pmayranicole@gmail.com', '1132187231', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '425662320', NULL, NULL),
(225, 'Camilo Ernesto', 'Puglisi', 'camilo-puglisi@hotmail.com', '01159719564', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '417033780', NULL, NULL),
(226, 'Natalia', 'Zarate', 'Zaratenatu22@gmail.com', '1138192883', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '458945160', NULL, NULL),
(227, 'Neson', 'Montaño Rodriguez', 'nelsonuai2017@gmail.com', '1159438418', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '938826840', NULL, NULL),
(228, 'Agustina', 'Romero', 'romeroagustina602@gmail.com', '1162972757', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '452259460', NULL, NULL),
(229, 'Tadeo', 'Carballo', 'Urieldecarp912@mail.com', '1168512569', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '479544540', NULL, NULL),
(230, 'Mia Magali', 'Toranzo', 'Toranzomia588@gmail.com', '1130172392', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '468241300', NULL, NULL),
(231, 'Tamara', 'Galeano', 'Tamara6galeano@gmail.com', '1130030613', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '467448400', NULL, NULL),
(232, 'Gonzalo Gabriel', 'Medina', 'gonzaloperalta947@gmail.com', '1140697675', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '457356350', NULL, NULL),
(233, 'Blas', 'De Maria', 'blasdemaria@gmail.com', '1126855392', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '442556470', NULL, NULL),
(234, 'ABRIL ANTONELLA', 'CACERES', 'caceresabril616@gmail.com', '1123756393', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '459098270', NULL, NULL),
(235, 'Flora', 'Báez Delvalle', 'florabaez3095@gmail.com', '1126830906', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '949431230', NULL, NULL),
(236, 'Thomas Agustín', 'Gómez', 'thomygomez36@gmail.com', '+541170396241', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '457354440', NULL, NULL),
(237, 'nahuel', 'calloni', 'transporte.calltruck@hotmail.com', '1137797864', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '416929880', NULL, NULL),
(238, 'Lucas Agustin', 'Zepeda', 'lucaszepedaa8@gmail.com', '1164995650', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '419876810', NULL, NULL),
(239, 'Jesica Celeste', 'Rivero', 'cristobal06052020@gmail.com', '1156074931', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '407481170', NULL, NULL),
(240, 'Leonardo', 'Rodríguez', 'cristobal.14.01.1991@gmail.com', '1172104581', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '360654160', NULL, NULL),
(241, 'Barbara Agustina', 'bustos', 'bustosagustina005@gmail.com', '1127540389', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '386199020', NULL, NULL),
(242, 'candela Evelyn', 'ciriza Garay', 'candelaciriza2@gmail.com', '1157225255', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '463575480', NULL, NULL),
(243, 'Maitena', 'Picabea', 'm.x.y.1612@gmail.com', '1134433577', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '462782030', NULL, NULL),
(244, 'Lucia Marina', 'Vera', 'chapipasion@gmail.com', '1130200754', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '410648660', NULL, NULL),
(245, 'Diego Luis', 'Vera', 'diegovera1158@hotmail.com', '1158249835', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '230229670', NULL, NULL),
(246, 'Sergio Daniel', 'Serrano', 'sserrano@oca.com.ar', '1158090922', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(247, 'Rodrigo Alejandro', 'Lobo', 'rodrigo.lobo5454@gmail.com', '1134572790', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '435699520', NULL, NULL),
(248, 'Rocío Antonella', 'Silva', 'ro.319120@gmail.com', '1151778381', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '367027010', NULL, NULL),
(249, 'Fabiana Bellen', 'Kasinskas', 'fabianakasinskas@gmail.com', '1167940286', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '407702880', NULL, NULL),
(250, 'Julieta Leonor', 'Irala', 'judifali81@gmail.com', '1163567081', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '289077090', NULL, NULL),
(251, 'Lucia', 'Ruiz', 'luciabruiz@gmail.com', '1165492045', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '315314330', NULL, NULL),
(252, 'Gustavo', 'Abrego', 'gustavodabrego@gmail.com', '1165274579', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '329699790', NULL, NULL),
(253, 'Gonzalo', 'Flores', 'gonzalo.flores@ypf.com', '2215903543', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '317435560', NULL, NULL),
(254, 'Priscila', 'Vera', 'priscilavera457@gmail.com', '+541137757060', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '467576360', NULL, NULL);
INSERT INTO api_asistente (id, first_name, last_name, email, phone, profile_type, asistencia_confirmada, fecha_confirmacion, rol_especifico, dni_update_token, dni_email_sent, dni_email_sent_date, terminos_aceptados, ciudad_provincia, disertante_vinculado_id, empresa_vinculada_id, fecha_registro, dni, representante_grupo_id, prensa_vinculada_id) VALUES
(255, 'Gabriela Soledad', 'Gonzalez', 'gabyyelias14@gmail.com', '1127853073', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '190842020', NULL, NULL),
(256, 'Gabriel Antonio', 'Monzon', 'gmgabrielmonzon@gmail.com', '2215774179', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '399454960', NULL, NULL),
(257, 'Roxana', 'sotelo', 'roxanasoteloangelik94@gmail.com', '1158780155', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '391050240', NULL, NULL),
(258, 'Micaela Agustina', 'Villanueva', 'Micaelavillanueva817@gmail.com', '1169242549', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '408813880', NULL, NULL),
(259, 'Lorena Anabella', 'Rios', 'anabellarios37@gmail.com', '1133666518', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '379863840', NULL, NULL),
(260, 'Gonzalo', 'roldan', 'Roldangonzalo2710@gmail.com', '+542224412509', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '467395540', NULL, NULL),
(261, 'Matias', 'ezequiel', 'Villarrealmatiasezequiel99@gmail.com', '1155919275', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '453003270', NULL, NULL),
(262, 'Yanina Itati', 'Monzon', 'yaniimonzon1@gmail.con', '1158918701', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '318270690', NULL, NULL),
(263, 'Gonzalo', 'Esteban', 'gonzadavila11@gmail.com', '01141404983', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '429076470', NULL, NULL),
(264, 'Enzo', 'marecos', 'Marecosenzo@gmail.com', '1131021202', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '438158040', NULL, NULL),
(265, 'León Martiniano', 'Godoy', 'leongodoy2017@gmail.com', '+5491144369843', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '445932720', NULL, NULL),
(266, 'Claudio Dario', 'García', 'garciaclaudio280@gmail.com', '1165363221', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '226156110', NULL, NULL),
(267, 'Luna Nair', 'Amaya', 'Amayalunanair@gmail.com', '1176256493', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '471439420', NULL, NULL),
(268, 'juan Gabriel', 'martinez', 'jgmartinez9520@gmail.com', '1139092923', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '392704820', NULL, NULL),
(269, 'Florencia', 'Argañaraz', 'florenciaarganarazs44@gmail.com', '2224576488', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '433894880', NULL, NULL),
(270, 'Elizabeth Soledad', 'fasa', 'selefasa09@gmail.com', '1138585459', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '353219070', NULL, NULL),
(271, 'Florencia', 'Soffiantini', 'fsoffiantini@gmail.com', '01136314088', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '397590330', NULL, NULL),
(272, 'rocio', 'mazzeo', 'uvita.mazzeo@gmail.com', '1167265482', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '377866380', NULL, NULL),
(273, 'Sonia Alicia', 'Taco', 'sonyatacko@gmail.com', '1122926084', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '251270840', NULL, NULL),
(274, 'Daniela Alejandra', 'Morello', 'tecnicalogistica92@gmail.com', '2224540862', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '366616190', NULL, NULL),
(275, 'Fernando Jesus', 'Jamardo', 'fernandojesusjamardo@gmail.com', '01137770396', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '228754500', NULL, NULL),
(276, 'Federico Hernan', 'Sanchez', 'fedesanchex98@gmail.com', '1156649528', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '409170790', NULL, NULL),
(277, 'PABLO Gaston', 'CURUCHET', 'PABLOCURUC@GMAIL.COM', '1149453960', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '347629370', NULL, NULL),
(278, 'Victoria Mariana', 'vera', 'Mariana.vera1216@gmail.com', '1132781079', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '366612810', NULL, NULL),
(279, 'Luciano Samuel', 'Rodríguez Taboada', 'taboadasamuel2002@gmail.com', '1171521179', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '44051968', NULL, NULL),
(280, 'Sebastian', 'Gomez', 'sebastiangomez31854@gmail.com', '01130447627', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '369182410', NULL, NULL),
(281, 'Joaquin Alejandro', 'Jara', 'jara.joaquin.alejandro@gmail.com', '01162550997', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '296008860', NULL, NULL),
(282, 'Gonzalo', 'Rubbo', 'gonzalomrubbo@gmail.com', '1160169283', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '386111540', NULL, NULL),
(283, 'Tomas Ignacio', 'Arias', 'Tomasignacioarias2005@gmail.com', '1124013734', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '468296420', NULL, NULL),
(284, 'Anibal Alejandro', 'porchia', 'Aporchia80@gmail.com', '1132403135', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '280669950', NULL, NULL),
(285, 'Carla Leticia', 'Gerol', 'gerolcarla@gmail.com', '1553841149', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '309409260', NULL, NULL),
(286, 'Lisandro', 'Lopez Agostoni', 'lisandroagostoni888@gmail.com', '1140951853', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '452259220', NULL, NULL),
(287, 'Cesar', 'Dominguez Larross', 'Larrosa16121977@gmail.com', '1123595037', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '930405880', NULL, NULL),
(288, 'Demian Agustin', 'Duarte', 'duartedemian02@gmail.com', '1124521908', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '443375970', NULL, NULL),
(289, 'Mariano', 'Alturria', 'marianoalturriaa@gmail.com', '1125215097', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '429600250', NULL, NULL),
(290, 'Fabián Nahuel', 'Ojeda', 'fabydc19@gmail.com', '1165106949', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '357197280', NULL, NULL),
(291, 'Jonathan David', 'Espinola Guzman', 'jondavidespinola@gmail.com', '1155650975', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '330796190', NULL, NULL),
(292, 'Daniela Carolina', 'Aguilar Castillo', 'adanielaaguilar1@gmail.com', '1158214020', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '952653350', NULL, NULL),
(293, 'Cecilia', 'velazquez', 'Cecivelazquez875@gmail.com', '541135895893', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '468284490', NULL, NULL),
(294, 'Maria Elena', 'Rosales', 'mariasantijuanpi@gmail.com', '1156589820', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '294385040', NULL, NULL),
(295, 'Sergio Alejandro Agustin', 'Bonavera', 'sergioobonnavera@gmail.com', '1158915461', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '453971490', NULL, NULL),
(296, 'Jorge', 'Vera', 'George2305@live.com.ar', '1169527181', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '226349950', NULL, NULL),
(297, 'Gabriel', 'Ayala Colman', 'Gabrielayalacolman@gmail.com', '1159708243', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '284599110', NULL, NULL),
(298, 'Larisa Valeria', 'Vazquez', 'larisavazquez21@gmail.com', '1137957617', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '392812300', NULL, NULL),
(299, 'Cristina Elisabeth', 'Villagra', 'elyvillagra91@gmail.com', '3812511073', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '366126100', NULL, NULL),
(300, 'Federico', 'Brugnoli', 'fedewasii@gmail.com', '1151479076', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '419140160', NULL, NULL),
(301, 'Brenda Macarena', 'Butron', 'brenbutron83@gmail.com', '2224505537', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '426219800', NULL, NULL),
(302, 'Luz Agustina Rocio', 'Godoy', 'agustino.godoy@gmail.com', '1132735575', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '461985960', NULL, NULL),
(303, 'Nicolás Daniel', 'Antunez', 'NsAntunez@gmail.com', '1126344635', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '388910900', NULL, NULL),
(304, 'Damian Maximiliano', 'galetto', 'Damiangaletto72@gmail.com', '1140332695', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '361548270', NULL, NULL);
INSERT INTO api_asistente (id, first_name, last_name, email, phone, profile_type, asistencia_confirmada, fecha_confirmacion, rol_especifico, dni_update_token, dni_email_sent, dni_email_sent_date, terminos_aceptados, ciudad_provincia, disertante_vinculado_id, empresa_vinculada_id, fecha_registro, dni, representante_grupo_id, prensa_vinculada_id) VALUES
(305, 'Natalia', 'Leiva', 'nati.leiva93@gmail.com', '1134150642', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '374773380', NULL, NULL),
(306, 'Elizabeth', 'Guzman', 'eli.g2514@gmail.com', '1167525541', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '389337420', NULL, NULL),
(307, 'Agustin Roberto', 'Juarez', 'agustinj_87@hotmail.com', '01161014090', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '328719210', NULL, NULL),
(308, 'Sebastián Ariel', 'Murua', 'seba24041999@gmail.com', '1158368193', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '420121170', NULL, NULL),
(309, 'Nicolás Urial', 'Castro', 'nc17365@gmail.com', '1166633982', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '458954750', NULL, NULL),
(310, 'Miguel', 'Davter', 'miguel.davter@gmail.com', '01133407314', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '210049940', NULL, NULL),
(311, 'Javier Alejandro', 'Deleo', 'aledeleo1985@gmail.com', '1134446775', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '317568550', NULL, NULL),
(312, 'Federico', 'Garay', 'Garay.federico@hotmail.com', '3484693752', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '378785660', NULL, NULL),
(313, 'Angel Dario', 'Acosta Roldan', 'dario201296@gmail.com', '1169664787', 'STUDENT', FALSE, NULL, 'Staff o Colaborador', NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '946974470', NULL, NULL),
(314, 'Maximiliano', 'Roldán', 'maxivannoni05@gmail.com', '541570213560', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '388448190', NULL, NULL),
(315, 'Lucas', 'Crivelli', 'lucas.crivelli12@gmail.com', '+5491168144855', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '392077050', NULL, NULL),
(316, 'Ezequiel Maximiliano', 'Zarauz', 'info@postalmas.com.ar', '1125551495', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '360662670', NULL, NULL),
(317, 'Daiana Anabela', 'Silva Valdez', 'daisilvavaldezz@gmail.com', '1133425469', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '358027660', NULL, NULL),
(318, 'Walter', 'Iglesias', 'Wiglesias@gta.com.ar', '1166057289', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '240757150', NULL, NULL),
(319, 'Hernán', 'Waldemar Ockstat', 'waldemar.ockstat@gmail.com', '3496514264', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '266105330', NULL, NULL),
(320, 'Maria Antonieta', 'Ruiz Fernández', 'mantonieta.ruizf@gmail.com', '2216405145', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '960944500', NULL, NULL),
(321, 'German Antonio', 'faldetta', 'german.faldetta@hotmail.com', '1149796034', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '352049210', NULL, NULL),
(322, 'Leonardo Daniel Marín', 'Aranda', 'Leonardo.aranda.m1@gmail.com', '1166501207', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '961176800', NULL, NULL),
(323, 'tomas', 'cufre', 'tomas.a.cufre@gmail.com', '1139383290', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '421181150', NULL, NULL),
(324, 'JUAN Cruz', 'SARNO FINELLI', 'Juansarno1@gmail.com', '3537487651', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '387296160', NULL, NULL),
(325, 'Silva Myrna', 'Evelin', 'myrnaevelin.ms@gmail.com', '0111564567192', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '360844550', NULL, NULL),
(326, 'Juliana', 'Ferreyra', 'julianagferreyra@gmail.com', '1150373133', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '346306040', NULL, NULL),
(327, 'Candela Anahi', 'Jordan Garcia', 'candelajordan.estudio@gmail.com', '1127266714', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '462925610', NULL, NULL),
(328, 'Milagros Lara Belen', 'Pintos', 'milupintos07@gmail.com', '1135723682', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '478775520', NULL, NULL),
(329, 'Nicolas Daniel', 'Gazcon', 'nicolas.gazcon@hotmail.com', '1136191454', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '285375880', NULL, NULL),
(330, 'Sergio Macerlo', 'Duarte', 'S.duarte@vemart.com.ar', '01131266263', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '267482520', NULL, NULL),
(331, 'Gerardo Emmanuel', 'Albornoz', 'gerardoealbornoz@gmail.com', '1123255604', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '330667340', NULL, NULL),
(332, 'Facundo', 'Diaz', 'Nicodiazgraff@gmail.com', '1165331033', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '443953850', NULL, NULL),
(333, 'Marcos Roberto', 'Lacapre', 'mcotratienpo@gmail.com', '01168588320', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '334187070', NULL, NULL),
(334, 'Lucas Matias', 'coria', 'lcoria86@hotmail.com', '1128856532', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '326546860', NULL, NULL),
(335, 'Beltrandi', 'Daiana', 'teobastiangarcia@gmail.com', '01144068077', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '359966560', NULL, NULL),
(336, 'Claudia', 'Mariel', 'cmd.mad.0307@gmail.com', '1132353179', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '324406120', NULL, NULL),
(337, 'Mayra yamila', 'gimenez', 'mgimenezdiazz@gmail.com', '1133022422', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '391072360', NULL, NULL),
(338, 'Jose Luis', 'Garnica Torricos', 'Joseluisgarnicatorricos@gmail.com', '1170279389', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '204113040', NULL, NULL),
(339, 'Julián Gabriel', 'Luna', 'julianluna276@gmail.com', '541150974727', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '454968710', NULL, NULL),
(340, 'Adolfo Gustavo', 'iglesias', 'rutasargentinas.1963@gmail.com', '01140349510', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '169779250', NULL, NULL),
(341, 'Juan Francisco', 'bortolamedi', 'Juanbortolamedioasis@gmail.com', '1151794178', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '360874800', NULL, NULL),
(342, 'Maximiliano Agustin', 'Blanco', 'maxyblanco92@gmail.com', '1140572971', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '368944020', NULL, NULL),
(343, 'Martin Facundo', 'Gordon', 'martingordon301@gmail.com', '0111526687783', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', NULL, NULL, NULL),
(344, 'Luis', 'Efraín Gil Riera', 'Luisgiltsu@gmail.com', '2215379302', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '958535220', NULL, NULL),
(345, 'Facundo Ezequiel', 'Sotelo', 'sotelofacundo339@gmail.com', '+541162185419', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '456727000', NULL, NULL),
(346, 'Matias Ezequiel', 'Garcia Tortosa', 'matiasgarcia1412@gmail.com', '1165208972', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '422485460', NULL, NULL),
(347, 'Florencia Soledad', 'Toledo', 'toledoflorencia.ft@gmail.com', '1172373461', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '368976660', NULL, NULL),
(348, 'Darío Sebastián', 'Gimenez', 'dgimenez.developer@gmail.com', '32522833', 'VISITOR', TRUE, '2025-11-15 12:40:28', NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '32522833', NULL, NULL),
(352, 'Lucas', 'Echavarria', 'echavarrialucas1986@gmail.com', '1131078008', 'VISITOR', FALSE, NULL, NULL, NULL, FALSE, NULL, FALSE, NULL, NULL, NULL, '2026-03-13 03:20:34.945596', '32764773', NULL, NULL);

-- Estructura para api_programa
CREATE TABLE api_programa (id integer NOT NULL PRIMARY KEY , titulo VARCHAR(255) NOT NULL, hora_inicio time NOT NULL, hora_fin time NOT NULL, dia date NOT NULL, descripcion text NOT NULL, aula VARCHAR(30) NOT NULL, categoria VARCHAR(30) NOT NULL);

INSERT INTO api_programa (id, titulo, hora_inicio, hora_fin, dia, descripcion, aula, categoria) VALUES
(267, 'Radio Red Logística', '14:00:00', '15:30:00', '2025-11-15', 'Transmisión en vivo del evento.', 'Aula Magna', 'RADIO'),
(272, 'Charla de Jorge Golfieri en Aula 1 (1h)', '10:00:00', '11:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Jorge Golfieri en Aula 1 a las 10:00, duración 1h.', 'Aula 1', 'TRANSPORTE'),
(273, 'Charla de Juan Sanchez en Aula 1 (1h30m)', '11:30:00', '13:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Juan Sanchez en Aula 1 a las 11:30, duración 1h30m.', 'Aula 1', 'SOSTENIBILIDAD'),
(274, 'Charla de Martin Boris en Aula 1 (1h)', '13:30:00', '14:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Martin Boris en Aula 1 a las 13:30, duración 1h.', 'Aula 1', 'INNOVACIÓN'),
(275, 'Charla de Gabriel Luchessi en Aula 1 (1h30m)', '15:00:00', '16:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Gabriel Luchessi en Aula 1 a las 15:00, duración 1h30m.', 'Aula 1', 'TRANSPORTE'),
(276, 'Charla de Delfina Salgado en Aula 1 (1h)', '17:00:00', '18:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Delfina Salgado en Aula 1 a las 17:00, duración 1h.', 'Aula 1', 'SOSTENIBILIDAD'),
(277, 'Charla de Juan Sanchez en Aula 2 (1h)', '10:00:00', '11:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Juan Sanchez en Aula 2 a las 10:00, duración 1h.', 'Aula 2', 'SUPPLY CHAIN'),
(278, 'Charla de Martin Boris en Aula 2 (1h30m)', '11:30:00', '13:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Martin Boris en Aula 2 a las 11:30, duración 1h30m.', 'Aula 2', 'TECNOLOGÍA'),
(279, 'Charla de Gabriel Luchessi en Aula 2 (1h)', '13:30:00', '14:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Gabriel Luchessi en Aula 2 a las 13:30, duración 1h.', 'Aula 2', 'GESTIÓN'),
(280, 'Charla de Delfina Salgado en Aula 2 (1h30m)', '15:00:00', '16:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Delfina Salgado en Aula 2 a las 15:00, duración 1h30m.', 'Aula 2', 'SUPPLY CHAIN'),
(281, 'Charla de Federico Carlos en Aula 2 (1h)', '17:00:00', '18:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Federico Carlos en Aula 2 a las 17:00, duración 1h.', 'Aula 2', 'TECNOLOGÍA'),
(282, 'Charla de Martin Boris en Aula 3 (1h)', '10:00:00', '11:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Martin Boris en Aula 3 a las 10:00, duración 1h.', 'Aula 3', 'TECNOLOGÍA'),
(283, 'Charla de Gabriel Luchessi en Aula 3 (1h30m)', '11:30:00', '13:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Gabriel Luchessi en Aula 3 a las 11:30, duración 1h30m.', 'Aula 3', 'INNOVACIÓN'),
(284, 'Charla de Delfina Salgado en Aula 3 (1h)', '13:30:00', '14:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Delfina Salgado en Aula 3 a las 13:30, duración 1h.', 'Aula 3', 'LOGÍSTICA'),
(285, 'Charla de Federico Carlos en Aula 3 (1h30m)', '15:00:00', '16:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Federico Carlos en Aula 3 a las 15:00, duración 1h30m.', 'Aula 3', 'TECNOLOGÍA'),
(286, 'Charla de Diego Plumaris en Aula 3 (1h)', '17:00:00', '18:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Diego Plumaris en Aula 3 a las 17:00, duración 1h.', 'Aula 3', 'INNOVACIÓN'),
(287, 'Charla de Gabriel Luchessi en Aula 4 (1h)', '10:00:00', '11:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Gabriel Luchessi en Aula 4 a las 10:00, duración 1h.', 'Aula 4', 'SOSTENIBILIDAD'),
(288, 'Charla de Delfina Salgado en Aula 4 (1h30m)', '11:30:00', '13:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Delfina Salgado en Aula 4 a las 11:30, duración 1h30m.', 'Aula 4', 'GESTIÓN'),
(289, 'Charla de Federico Carlos en Aula 4 (1h)', '13:30:00', '14:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Federico Carlos en Aula 4 a las 13:30, duración 1h.', 'Aula 4', 'NETWORKING'),
(290, 'Charla de Diego Plumaris en Aula 4 (1h30m)', '15:00:00', '16:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Diego Plumaris en Aula 4 a las 15:00, duración 1h30m.', 'Aula 4', 'SOSTENIBILIDAD'),
(291, 'Charla de Cristian Ruiz en Aula 4 (1h)', '17:00:00', '18:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Cristian Ruiz en Aula 4 a las 17:00, duración 1h.', 'Aula 4', 'GESTIÓN'),
(292, 'Charla de Delfina Salgado en Aula 5 (1h)', '10:00:00', '11:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Delfina Salgado en Aula 5 a las 10:00, duración 1h.', 'Aula 5', 'INNOVACIÓN'),
(293, 'Charla de Federico Carlos en Aula 5 (1h30m)', '11:30:00', '13:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Federico Carlos en Aula 5 a las 11:30, duración 1h30m.', 'Aula 5', 'TECNOLOGÍA'),
(294, 'Charla de Diego Plumaris en Aula 5 (1h)', '13:30:00', '14:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Diego Plumaris en Aula 5 a las 13:30, duración 1h.', 'Aula 5', 'SUPPLY CHAIN'),
(295, 'Charla de Cristian Ruiz en Aula 5 (1h30m)', '15:00:00', '16:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Cristian Ruiz en Aula 5 a las 15:00, duración 1h30m.', 'Aula 5', 'INNOVACIÓN'),
(296, 'Charla de Natalia Gonzalez en Aula 5 (1h)', '17:00:00', '18:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Natalia Gonzalez en Aula 5 a las 17:00, duración 1h.', 'Aula 5', 'TECNOLOGÍA'),
(297, 'Charla de Federico Carlos en Aula 6 (1h)', '10:00:00', '11:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Federico Carlos en Aula 6 a las 10:00, duración 1h.', 'Aula 6', 'GESTIÓN'),
(298, 'Charla de Diego Plumaris en Aula 6 (1h30m)', '11:30:00', '13:00:00', '2025-09-10', 'Descripción de ejemplo para la charla de Diego Plumaris en Aula 6 a las 11:30, duración 1h30m.', 'Aula 6', 'TRANSPORTE'),
(299, 'Charla de Cristian Ruiz en Aula 6 (1h)', '13:30:00', '14:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Cristian Ruiz en Aula 6 a las 13:30, duración 1h.', 'Aula 6', 'LOGÍSTICA'),
(300, 'Charla de Natalia Gonzalez en Aula 6 (1h30m)', '15:00:00', '16:30:00', '2025-09-10', 'Descripción de ejemplo para la charla de Natalia Gonzalez en Aula 6 a las 15:00, duración 1h30m.', 'Aula 6', 'GESTIÓN'),
(301, 'CLAUDIA FREED - INTERNACIONAL', '10:00:00', '11:00:00', '2025-11-15', 'Revolucionando la Logística: De la Economía Circular a la Transformación Digital', 'Aula 1', 'SUSTENTABILIDAD');

-- Estructura para api_programa_disertantes
CREATE TABLE api_programa_disertantes (id integer NOT NULL PRIMARY KEY , programa_id bigint NOT NULL REFERENCES api_programa (id) DEFERRABLE INITIALLY DEFERRED, disertante_id bigint NOT NULL REFERENCES api_disertante (id) DEFERRABLE INITIALLY DEFERRED);

-- Estructura para api_inscripcion
CREATE TABLE api_inscripcion (id integer NOT NULL PRIMARY KEY , fecha_inscripcion TIMESTAMP NOT NULL, asistente_id bigint NOT NULL REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED, empresa_id bigint NULL REFERENCES api_empresa (id) DEFERRABLE INITIALLY DEFERRED, edicion_id bigint NOT NULL REFERENCES api_edicion (id) DEFERRABLE INITIALLY DEFERRED);

INSERT INTO api_inscripcion (id, fecha_inscripcion, asistente_id, empresa_id, edicion_id) VALUES
(16, '2026-03-08 20:22:58.541446', 352, NULL, 1),
(17, '2026-03-09 19:02:23.976510', 352, NULL, 2);

-- Estructura para api_certificado
CREATE TABLE api_certificado (id integer NOT NULL PRIMARY KEY , tipo_certificado VARCHAR(10) NOT NULL, pdf_generado VARCHAR(100) NULL, fecha_generacion TIMESTAMP NOT NULL, asistente_id bigint NOT NULL REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED);

INSERT INTO api_certificado (id, tipo_certificado, pdf_generado, fecha_generacion, asistente_id) VALUES
(3, 'ASISTENCIA', 'certificados/certificado_dgimenez_yJ0mqWP.developergmail.com.pdf', '2025-11-11 12:05:16.278855', 348);

-- Estructura para api_miembrogrupo
CREATE TABLE api_miembrogrupo (id integer NOT NULL PRIMARY KEY , full_name VARCHAR(200) NOT NULL, dni VARCHAR(10) NOT NULL, representante_id bigint NOT NULL REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED);

-- Estructura para api_detallegrupo
CREATE TABLE api_detallegrupo (id integer NOT NULL PRIMARY KEY , group_name VARCHAR(255) NULL, group_municipality VARCHAR(255) NULL, group_size integer NOT NULL, asistente_id bigint NOT NULL UNIQUE REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED, institution_or_workplace VARCHAR(255) NULL, tipo_grupo text NOT NULL );

-- Estructura para api_detalledocente
CREATE TABLE api_detalledocente (id integer NOT NULL PRIMARY KEY , institution VARCHAR(255) NULL, career_taught VARCHAR(255) NULL, asistente_id bigint NOT NULL UNIQUE REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED);

INSERT INTO api_detalledocente (id, institution, career_taught, asistente_id) VALUES
(1, NULL, NULL, 47),
(2, NULL, NULL, 96);

-- Estructura para api_detalleestudiante
CREATE TABLE api_detalleestudiante (id integer NOT NULL PRIMARY KEY , is_unab_student BOOLEAN NOT NULL, institution VARCHAR(255) NULL, career VARCHAR(255) NULL, year_of_study integer NULL, asistente_id bigint NOT NULL UNIQUE REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED);

INSERT INTO api_detalleestudiante (id, is_unab_student, institution, career, year_of_study, asistente_id) VALUES
(1, FALSE, NULL, NULL, NULL, 6),
(2, FALSE, NULL, NULL, NULL, 11),
(3, FALSE, NULL, NULL, NULL, 12),
(4, FALSE, NULL, NULL, NULL, 18),
(5, FALSE, NULL, NULL, NULL, 20),
(6, FALSE, NULL, NULL, NULL, 24),
(7, FALSE, NULL, NULL, NULL, 26),
(8, FALSE, NULL, NULL, NULL, 28),
(9, FALSE, NULL, NULL, NULL, 33),
(10, FALSE, NULL, NULL, NULL, 35),
(11, FALSE, NULL, NULL, NULL, 39),
(12, FALSE, NULL, NULL, NULL, 40),
(13, FALSE, NULL, NULL, NULL, 44),
(14, FALSE, NULL, NULL, NULL, 48),
(15, FALSE, NULL, NULL, NULL, 49),
(16, FALSE, NULL, NULL, NULL, 51),
(17, FALSE, NULL, NULL, NULL, 58),
(18, FALSE, NULL, NULL, NULL, 62),
(19, FALSE, NULL, NULL, NULL, 63),
(20, FALSE, NULL, NULL, NULL, 64),
(21, FALSE, NULL, NULL, NULL, 65),
(22, FALSE, NULL, NULL, NULL, 66),
(23, FALSE, NULL, NULL, NULL, 70),
(24, FALSE, NULL, NULL, NULL, 71),
(25, FALSE, NULL, NULL, NULL, 72),
(26, FALSE, NULL, NULL, NULL, 73),
(27, FALSE, NULL, NULL, NULL, 113),
(28, FALSE, NULL, NULL, NULL, 150),
(29, FALSE, NULL, NULL, NULL, 190),
(30, FALSE, NULL, NULL, NULL, 208),
(31, FALSE, NULL, NULL, NULL, 214),
(32, FALSE, NULL, NULL, NULL, 215),
(33, FALSE, NULL, NULL, NULL, 241),
(34, FALSE, NULL, NULL, NULL, 247),
(35, FALSE, NULL, NULL, NULL, 292),
(36, FALSE, NULL, NULL, NULL, 303),
(37, FALSE, NULL, NULL, NULL, 313);

-- Estructura para api_detalleprofesional
CREATE TABLE api_detalleprofesional (id integer NOT NULL PRIMARY KEY , work_area VARCHAR(255) NULL, occupation VARCHAR(255) NULL, asistente_id bigint NOT NULL UNIQUE REFERENCES api_asistente (id) DEFERRABLE INITIALLY DEFERRED);

INSERT INTO api_detalleprofesional (id, work_area, occupation, asistente_id) VALUES
(1, NULL, NULL, 123);

SET session_replication_role = 'origin';

-- Sincronización de secuencias
SELECT setval(pg_get_serial_sequence('django_content_type', 'id'), COALESCE(MAX(id), 1)) FROM django_content_type;
SELECT setval(pg_get_serial_sequence('auth_group', 'id'), COALESCE(MAX(id), 1)) FROM auth_group;
SELECT setval(pg_get_serial_sequence('auth_user', 'id'), COALESCE(MAX(id), 1)) FROM auth_user;
SELECT setval(pg_get_serial_sequence('api_edicion', 'id'), COALESCE(MAX(id), 1)) FROM api_edicion;
SELECT setval(pg_get_serial_sequence('django_migrations', 'id'), COALESCE(MAX(id), 1)) FROM django_migrations;
SELECT setval(pg_get_serial_sequence('auth_permission', 'id'), COALESCE(MAX(id), 1)) FROM auth_permission;
SELECT setval(pg_get_serial_sequence('auth_group_permissions', 'id'), COALESCE(MAX(id), 1)) FROM auth_group_permissions;
SELECT setval(pg_get_serial_sequence('auth_user_groups', 'id'), COALESCE(MAX(id), 1)) FROM auth_user_groups;
SELECT setval(pg_get_serial_sequence('auth_user_user_permissions', 'id'), COALESCE(MAX(id), 1)) FROM auth_user_user_permissions;
SELECT setval(pg_get_serial_sequence('django_admin_log', 'id'), COALESCE(MAX(id), 1)) FROM django_admin_log;
SELECT setval(pg_get_serial_sequence('api_disertante', 'id'), COALESCE(MAX(id), 1)) FROM api_disertante;
SELECT setval(pg_get_serial_sequence('api_inscripcionprensa', 'id'), COALESCE(MAX(id), 1)) FROM api_inscripcionprensa;
SELECT setval(pg_get_serial_sequence('api_empresa', 'id'), COALESCE(MAX(id), 1)) FROM api_empresa;
SELECT setval(pg_get_serial_sequence('api_postulaciondisertante', 'id'), COALESCE(MAX(id), 1)) FROM api_postulaciondisertante;
SELECT setval(pg_get_serial_sequence('api_asistente', 'id'), COALESCE(MAX(id), 1)) FROM api_asistente;
SELECT setval(pg_get_serial_sequence('api_programa', 'id'), COALESCE(MAX(id), 1)) FROM api_programa;
SELECT setval(pg_get_serial_sequence('api_programa_disertantes', 'id'), COALESCE(MAX(id), 1)) FROM api_programa_disertantes;
SELECT setval(pg_get_serial_sequence('api_inscripcion', 'id'), COALESCE(MAX(id), 1)) FROM api_inscripcion;
SELECT setval(pg_get_serial_sequence('api_certificado', 'id'), COALESCE(MAX(id), 1)) FROM api_certificado;
SELECT setval(pg_get_serial_sequence('api_miembrogrupo', 'id'), COALESCE(MAX(id), 1)) FROM api_miembrogrupo;
SELECT setval(pg_get_serial_sequence('api_detallegrupo', 'id'), COALESCE(MAX(id), 1)) FROM api_detallegrupo;
SELECT setval(pg_get_serial_sequence('api_detalledocente', 'id'), COALESCE(MAX(id), 1)) FROM api_detalledocente;
SELECT setval(pg_get_serial_sequence('api_detalleestudiante', 'id'), COALESCE(MAX(id), 1)) FROM api_detalleestudiante;
SELECT setval(pg_get_serial_sequence('api_detalleprofesional', 'id'), COALESCE(MAX(id), 1)) FROM api_detalleprofesional;
