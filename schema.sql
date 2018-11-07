drop table IF EXISTS register CASCADE;
drop table IF EXISTS register_tag CASCADE;
drop table IF EXISTS tag CASCADE;
drop table IF EXISTS post CASCADE;
drop table IF EXISTS post_tag CASCADE;
drop table IF EXISTS post_saved CASCADE;
drop table IF EXISTS picture CASCADE;
drop table IF EXISTS review CASCADE;

create table register (
	id SERIAL PRIMARY KEY,
	email varchar(100),
    name varchar(20),
	user_id varchar(255) UNIQUE,
    avator varchar(255) DEFAULT 'https://vignette.wikia.nocookie.net/pkmnshuffle/images/3/32/Psyduck.png/revision/latest?cb=20170407192426',
    description varchar(255),
    phone varchar(30),
    isDesigner boolean
);
create table tag (
	tag_id SERIAL PRIMARY KEY,
	name varchar(255),
	type varchar(100)
);


create table register_tag (
	id SERIAL PRIMARY KEY,
    register_id int references register,
    tag_id int references tag
);


create table post (
	post_id SERIAL PRIMARY KEY,
	publisher_id int references register,
	title varchar(255) NOT NULL,
	time timestamp,
	content text,
	status int,
	dealer_id int references register,
	location varchar(255) NOT NULL,
	budget int,
	area text,
	saved_times int DEFAULT 0,
	closed boolean DEFAULT FALSE,
	views int DEFAULT 0
);

create table post_tag (
    id SERIAL PRIMARY KEY,
    post_id int references post,
    tag_id int references tag
);

create table post_saved(
	saved_id SERIAL PRIMARY KEY,
	post_id int references post,
	user_id int references register
);

create table review (
	review_id SERIAL PRIMARY KEY,
	company_id int references register,
	reviewer_id int references register,
	post_id int references post,
	rate int NOT NULL,
	comment text,
	time timestamp
);

create table picture (
	picture_id SERIAL PRIMARY KEY,
	register_id int references register,
	post_id int references post,
	img bytea
);

