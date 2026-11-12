--
-- PostgreSQL database dump
--

\restrict j1eDBgvN3dKZsueIvhIQiaPP8fghJtPVAv5IFdLZdjBaMt9LSzxMhSTIa0K4JNF

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: bookings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bookings (
    id integer NOT NULL,
    room_id integer NOT NULL,
    user_id integer NOT NULL,
    date_from date NOT NULL,
    date_to date NOT NULL,
    price integer NOT NULL,
    CONSTRAINT ck_bookings_dates_valid CHECK ((date_to > date_from)),
    CONSTRAINT ck_bookings_price_positive CHECK ((price > 0))
);


ALTER TABLE public.bookings OWNER TO postgres;

--
-- Name: bookings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bookings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bookings_id_seq OWNER TO postgres;

--
-- Name: bookings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bookings_id_seq OWNED BY public.bookings.id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    inventory_number character varying(50) NOT NULL,
    name character varying(150) NOT NULL,
    category character varying(80) NOT NULL,
    description text,
    location character varying(150) NOT NULL,
    status character varying(20) DEFAULT 'available'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_equipment_status CHECK (((status)::text = ANY ((ARRAY['available'::character varying, 'issued'::character varying, 'maintenance'::character varying, 'retired'::character varying])::text[])))
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_id_seq OWNER TO postgres;

--
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- Name: facilities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.facilities (
    id integer NOT NULL,
    title character varying(100) NOT NULL
);


ALTER TABLE public.facilities OWNER TO postgres;

--
-- Name: facilities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.facilities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.facilities_id_seq OWNER TO postgres;

--
-- Name: facilities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.facilities_id_seq OWNED BY public.facilities.id;


--
-- Name: hotels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hotels (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    location character varying NOT NULL
);


ALTER TABLE public.hotels OWNER TO postgres;

--
-- Name: hotels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hotels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hotels_id_seq OWNER TO postgres;

--
-- Name: hotels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hotels_id_seq OWNED BY public.hotels.id;


--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    image_url character varying NOT NULL,
    source_image character varying NOT NULL
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.images_id_seq OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: maintenance_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.maintenance_records (
    id integer NOT NULL,
    equipment_id integer NOT NULL,
    reported_by integer NOT NULL,
    description text NOT NULL,
    status character varying(20) DEFAULT 'open'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    resolved_by integer,
    resolved_at timestamp with time zone,
    CONSTRAINT ck_maintenance_status CHECK (((status)::text = ANY ((ARRAY['open'::character varying, 'in_progress'::character varying, 'resolved'::character varying])::text[])))
);


ALTER TABLE public.maintenance_records OWNER TO postgres;

--
-- Name: maintenance_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.maintenance_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.maintenance_records_id_seq OWNER TO postgres;

--
-- Name: maintenance_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.maintenance_records_id_seq OWNED BY public.maintenance_records.id;


--
-- Name: reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservations (
    id integer NOT NULL,
    equipment_id integer NOT NULL,
    user_id integer NOT NULL,
    starts_at timestamp with time zone NOT NULL,
    ends_at timestamp with time zone NOT NULL,
    purpose text NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    approved_by integer,
    approved_at timestamp with time zone,
    issued_at timestamp with time zone,
    returned_at timestamp with time zone,
    CONSTRAINT ck_reservations_period CHECK ((ends_at > starts_at)),
    CONSTRAINT ck_reservations_status CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'rejected'::character varying, 'issued'::character varying, 'returned'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.reservations OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservations_id_seq OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservations_id_seq OWNED BY public.reservations.id;


--
-- Name: room_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.room_images (
    id integer NOT NULL,
    room_id integer NOT NULL,
    image_id integer NOT NULL
);


ALTER TABLE public.room_images OWNER TO postgres;

--
-- Name: room_images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.room_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.room_images_id_seq OWNER TO postgres;

--
-- Name: room_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.room_images_id_seq OWNED BY public.room_images.id;


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id integer NOT NULL,
    hotel_id integer NOT NULL,
    title character varying NOT NULL,
    description character varying,
    price integer NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT ck_rooms_price_positive CHECK ((price > 0)),
    CONSTRAINT ck_rooms_quantity_positive CHECK ((quantity >= 0))
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- Name: rooms_facilities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms_facilities (
    id integer NOT NULL,
    room_id integer NOT NULL,
    facility_id integer NOT NULL
);


ALTER TABLE public.rooms_facilities OWNER TO postgres;

--
-- Name: rooms_facilities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_facilities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rooms_facilities_id_seq OWNER TO postgres;

--
-- Name: rooms_facilities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_facilities_id_seq OWNED BY public.rooms_facilities.id;


--
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rooms_id_seq OWNER TO postgres;

--
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(100) NOT NULL,
    role character varying(20) DEFAULT 'student'::character varying NOT NULL,
    CONSTRAINT ck_users_role CHECK (((role)::text = ANY ((ARRAY['student'::character varying, 'technician'::character varying, 'admin'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: bookings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings ALTER COLUMN id SET DEFAULT nextval('public.bookings_id_seq'::regclass);


--
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- Name: facilities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.facilities ALTER COLUMN id SET DEFAULT nextval('public.facilities_id_seq'::regclass);


--
-- Name: hotels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hotels ALTER COLUMN id SET DEFAULT nextval('public.hotels_id_seq'::regclass);


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Name: maintenance_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_records ALTER COLUMN id SET DEFAULT nextval('public.maintenance_records_id_seq'::regclass);


--
-- Name: reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations ALTER COLUMN id SET DEFAULT nextval('public.reservations_id_seq'::regclass);


--
-- Name: room_images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_images ALTER COLUMN id SET DEFAULT nextval('public.room_images_id_seq'::regclass);


--
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- Name: rooms_facilities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms_facilities ALTER COLUMN id SET DEFAULT nextval('public.rooms_facilities_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
20261112_labgear
\.


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bookings (id, room_id, user_id, date_from, date_to, price) FROM stdin;
\.


--
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment (id, inventory_number, name, category, description, location, status, created_at, updated_at) FROM stdin;
1	string	string	string	string	string	available	2026-11-12 07:11:43.528101+00	2026-11-12 07:11:43.528101+00
2	LAB-001	Осциллограф Rigol DS1054Z	Измерительное оборудование	Цифровой осциллограф для исследования электрических сигналов	Лаборатория 204	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
3	LAB-002	Мультиметр UNI-T UT61E	Измерительное оборудование	Цифровой мультиметр для измерения напряжения, тока и сопротивления	Лаборатория 204	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
4	LAB-003	Генератор сигналов FY6900	Генераторы сигналов	Двухканальный генератор сигналов произвольной формы	Лаборатория 206	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
5	LAB-004	Источник питания Korad KA3005P	Источники питания	Лабораторный регулируемый источник питания 0–30 В	Лаборатория 206	issued	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
6	LAB-005	Микроскоп Levenhuk 500T	Оптическое оборудование	Тринокулярный микроскоп для учебных и исследовательских работ	Лаборатория 310	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
7	LAB-006	3D-принтер Creality Ender-3 V3	Производственное оборудование	Принтер для изготовления учебных прототипов и деталей	Мастерская 012	maintenance	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
8	LAB-007	Паяльная станция Quick 861DW	Паяльное оборудование	Термовоздушная паяльная станция для монтажа компонентов	Мастерская 012	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
9	LAB-008	Тепловизор UNI-T UTi260B	Диагностическое оборудование	Тепловизор для бесконтактной диагностики нагрева узлов	Лаборатория 208	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
10	LAB-009	3D-сканер Revopoint POP 3	Сканирующее оборудование	Компактный 3D-сканер для оцифровки физических объектов	Мастерская 014	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
11	LAB-010	Лабораторный блок питания OWON	Источники питания	Двухканальный источник питания для практических занятий	Лаборатория 204	available	2026-11-12 07:35:23.352008+00	2026-11-12 07:35:23.352008+00
\.


--
-- Data for Name: facilities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.facilities (id, title) FROM stdin;
\.


--
-- Data for Name: hotels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hotels (id, title, location) FROM stdin;
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.images (id, image_url, source_image) FROM stdin;
\.


--
-- Data for Name: maintenance_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.maintenance_records (id, equipment_id, reported_by, description, status, created_at, resolved_by, resolved_at) FROM stdin;
1	7	10	DEMO: Требуется калибровка оси X после перемещения принтера.	open	2026-11-12 07:35:23.352008+00	\N	\N
\.


--
-- Data for Name: reservations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservations (id, equipment_id, user_id, starts_at, ends_at, purpose, status, created_at, approved_by, approved_at, issued_at, returned_at) FROM stdin;
1	1	4	2026-11-13 07:00:00+00	2026-11-13 09:00:00+00	Использование оборудования для лабораторной работы	pending	2026-11-12 07:14:12.533564+00	\N	\N	\N	\N
2	2	9	2026-11-14 07:35:23.328143+00	2026-11-14 09:35:23.328143+00	Демонстрационная заявка: pending-oscilloscope	pending	2026-11-12 07:35:23.352008+00	\N	\N	\N	\N
3	3	10	2026-11-13 07:35:23.328143+00	2026-11-13 09:35:23.328143+00	Демонстрационная заявка: approved-multimeter	approved	2026-11-12 07:35:23.352008+00	8	2026-11-13 07:25:23.328143+00	\N	\N
4	5	9	2026-11-12 06:50:23.328143+00	2026-11-12 09:35:23.328143+00	Демонстрационная заявка: issued-power-supply	issued	2026-11-12 07:35:23.352008+00	8	2026-11-12 06:40:23.328143+00	2026-11-12 06:50:23.328143+00	\N
5	6	10	2026-11-07 04:35:23.328143+00	2026-11-07 06:35:23.328143+00	Демонстрационная заявка: returned-microscope	returned	2026-11-12 07:35:23.352008+00	8	2026-11-07 04:25:23.328143+00	2026-11-07 04:35:23.328143+00	2026-11-07 06:35:23.328143+00
6	4	9	2026-11-09 07:35:23.328143+00	2026-11-09 09:35:23.328143+00	Демонстрационная заявка: rejected-generator	rejected	2026-11-12 07:35:23.352008+00	\N	\N	\N	\N
\.


--
-- Data for Name: room_images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.room_images (id, room_id, image_id) FROM stdin;
\.


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rooms (id, hotel_id, title, description, price, quantity) FROM stdin;
\.


--
-- Data for Name: rooms_facilities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rooms_facilities (id, room_id, facility_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, hashed_password, role) FROM stdin;
1	admin@example.com	$2b$12$bEo8Q0rUiNnGF4f9wjjTbe0wAc/S78E.e2OBDicBho5yLx7yKarZi	admin
2	user@example.com	$2b$12$C6Eu4xtL4WlZLbfyvVxNQe48nQSDmt/ORHtj7CvVnDmE2Nv5FhKYq	student
4	admin@example1.com	$2b$12$jGPct9tup6iFGdfFD7MslO.fj.HkuXiru1LPzpUTkbEdaW1eqU5oa	student
6	admin@example.com	$2b$12$YsW3AlF0ttjRu.vm1ZD8aeWtvWmzQ7TDxA4760Yz0Ri2efQe84CZi	admin
7	admin@labgear.local	$2b$12$.ILtfRhNwgDyRJ5kt18PRuvYEOJFbDHke3piEqEwE.xnueP66qr.e	admin
8	technician@labgear.local	$2b$12$BdI/kcdedXwdAopsfSRlIeJE3niwmK.k7EnrSll.PMvZEAKba5Fva	technician
9	student@labgear.local	$2b$12$ZT1OrgfS/6mRGIMKCjy12.JmTnDxxEiVlSNvpO2gW1l0gQk7sbeEi	student
10	student2@labgear.local	$2b$12$F2dSwMrp0CikRUN4dYJiLusjynoOntsWpLNqz09Zl0CYL6NEFCJV6	student
11	admin@labgear.com	$2b$12$RoAAwsYmvHRVhrg1IsVA4OeHvEjo5zJleT4KsJlKjJ0kR2QifEOYW	admin
12	technician@labgear.com	$2b$12$.dYEyyw5.YR2kjgGQknK...E457.44JTmFL8yu9ELvmyZrVQK.M.m	technician
13	student@labgear.com	$2b$12$B7BYiQLoqKJDYyCiCGn4ruJL6SvQIRlUZ9C0fvDE3.i0Pyiz4KzCy	student
14	student2@labgear.com	$2b$12$WR9LTqFOWo8wI0e3zvrdJePkKKFeKXVSH.BI7Z4eKVqpXl9bDm52.	student
\.


--
-- Name: bookings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bookings_id_seq', 1, false);


--
-- Name: equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_id_seq', 11, true);


--
-- Name: facilities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.facilities_id_seq', 1, false);


--
-- Name: hotels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hotels_id_seq', 1, false);


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.images_id_seq', 1, false);


--
-- Name: maintenance_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.maintenance_records_id_seq', 1, true);


--
-- Name: reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservations_id_seq', 6, true);


--
-- Name: room_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.room_images_id_seq', 1, false);


--
-- Name: rooms_facilities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rooms_facilities_id_seq', 1, false);


--
-- Name: rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rooms_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 14, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- Name: facilities facilities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.facilities
    ADD CONSTRAINT facilities_pkey PRIMARY KEY (id);


--
-- Name: hotels hotels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hotels
    ADD CONSTRAINT hotels_pkey PRIMARY KEY (id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: maintenance_records maintenance_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_records
    ADD CONSTRAINT maintenance_records_pkey PRIMARY KEY (id);


--
-- Name: reservations reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_pkey PRIMARY KEY (id);


--
-- Name: room_images room_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_images
    ADD CONSTRAINT room_images_pkey PRIMARY KEY (id);


--
-- Name: rooms_facilities rooms_facilities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms_facilities
    ADD CONSTRAINT rooms_facilities_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: equipment uq_equipment_inventory_number; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT uq_equipment_inventory_number UNIQUE (inventory_number);


--
-- Name: rooms_facilities uq_room_facility; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms_facilities
    ADD CONSTRAINT uq_room_facility UNIQUE (room_id, facility_id);


--
-- Name: room_images uq_room_image; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_images
    ADD CONSTRAINT uq_room_image UNIQUE (room_id, image_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_equipment_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_equipment_category ON public.equipment USING btree (category);


--
-- Name: ix_equipment_category_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_equipment_category_status ON public.equipment USING btree (category, status);


--
-- Name: ix_equipment_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_equipment_name ON public.equipment USING btree (name);


--
-- Name: ix_maintenance_equipment_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_maintenance_equipment_status ON public.maintenance_records USING btree (equipment_id, status);


--
-- Name: ix_reservations_equipment_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservations_equipment_period ON public.reservations USING btree (equipment_id, starts_at, ends_at);


--
-- Name: ix_reservations_user_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservations_user_status ON public.reservations USING btree (user_id, status);


--
-- Name: bookings bookings_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);


--
-- Name: bookings bookings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: room_images fk_room_images_image_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_images
    ADD CONSTRAINT fk_room_images_image_id FOREIGN KEY (image_id) REFERENCES public.images(id) ON DELETE CASCADE;


--
-- Name: room_images fk_room_images_room_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_images
    ADD CONSTRAINT fk_room_images_room_id FOREIGN KEY (room_id) REFERENCES public.rooms(id) ON DELETE CASCADE;


--
-- Name: rooms_facilities fk_rooms_facilities_facility_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms_facilities
    ADD CONSTRAINT fk_rooms_facilities_facility_id FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: rooms_facilities fk_rooms_facilities_room_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms_facilities
    ADD CONSTRAINT fk_rooms_facilities_room_id FOREIGN KEY (room_id) REFERENCES public.rooms(id) ON DELETE CASCADE;


--
-- Name: maintenance_records maintenance_records_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_records
    ADD CONSTRAINT maintenance_records_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id) ON DELETE RESTRICT;


--
-- Name: maintenance_records maintenance_records_reported_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_records
    ADD CONSTRAINT maintenance_records_reported_by_fkey FOREIGN KEY (reported_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: maintenance_records maintenance_records_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_records
    ADD CONSTRAINT maintenance_records_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: reservations reservations_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: reservations reservations_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id) ON DELETE RESTRICT;


--
-- Name: reservations reservations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: rooms rooms_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id);


--
-- PostgreSQL database dump complete
--

\unrestrict j1eDBgvN3dKZsueIvhIQiaPP8fghJtPVAv5IFdLZdjBaMt9LSzxMhSTIa0K4JNF

