--
-- PostgreSQL database dump
--

-- Dumped from database version 14.6 (Homebrew)
-- Dumped by pg_dump version 14.6 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: Gender; Type: TYPE; Schema: public; Owner: Saud
--

CREATE TYPE public."Gender" AS ENUM (
    'Male',
    'Female'
);


ALTER TYPE public."Gender" OWNER TO "Saud";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actors; Type: TABLE; Schema: public; Owner: Saud
--

CREATE TABLE public.actors (
    id integer NOT NULL,
    name character varying,
    age integer,
    gender public."Gender",
    movie_id integer NOT NULL
);


ALTER TABLE public.actors OWNER TO "Saud";

--
-- Name: actors_id_seq; Type: SEQUENCE; Schema: public; Owner: Saud
--

CREATE SEQUENCE public.actors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.actors_id_seq OWNER TO "Saud";

--
-- Name: actors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Saud
--

ALTER SEQUENCE public.actors_id_seq OWNED BY public.actors.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: Saud
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO "Saud";

--
-- Name: movies; Type: TABLE; Schema: public; Owner: Saud
--

CREATE TABLE public.movies (
    id integer NOT NULL,
    title character varying,
    release_date date
);


ALTER TABLE public.movies OWNER TO "Saud";

--
-- Name: movies_id_seq; Type: SEQUENCE; Schema: public; Owner: Saud
--

CREATE SEQUENCE public.movies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.movies_id_seq OWNER TO "Saud";

--
-- Name: movies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Saud
--

ALTER SEQUENCE public.movies_id_seq OWNED BY public.movies.id;


--
-- Name: actors id; Type: DEFAULT; Schema: public; Owner: Saud
--

ALTER TABLE ONLY public.actors ALTER COLUMN id SET DEFAULT nextval('public.actors_id_seq'::regclass);


--
-- Name: movies id; Type: DEFAULT; Schema: public; Owner: Saud
--

ALTER TABLE ONLY public.movies ALTER COLUMN id SET DEFAULT nextval('public.movies_id_seq'::regclass);


--
-- Data for Name: actors; Type: TABLE DATA; Schema: public; Owner: Saud
--

COPY public.actors (id, name, age, gender, movie_id) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: Saud
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: movies; Type: TABLE DATA; Schema: public; Owner: Saud
--

COPY public.movies (id, title, release_date) FROM stdin;
\.


--
-- Name: actors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Saud
--

SELECT pg_catalog.setval('public.actors_id_seq', 1, false);


--
-- Name: movies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Saud
--

SELECT pg_catalog.setval('public.movies_id_seq', 1, true);


--
-- Name: actors actors_pkey; Type: CONSTRAINT; Schema: public; Owner: Saud
--

ALTER TABLE ONLY public.actors
    ADD CONSTRAINT actors_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: Saud
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: movies movies_pkey; Type: CONSTRAINT; Schema: public; Owner: Saud
--

ALTER TABLE ONLY public.movies
    ADD CONSTRAINT movies_pkey PRIMARY KEY (id);


--
-- Name: actors actors_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Saud
--

ALTER TABLE ONLY public.actors
    ADD CONSTRAINT actors_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id);


--
-- PostgreSQL database dump complete
--

