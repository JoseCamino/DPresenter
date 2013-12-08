CREATE TABLE user_list(FName text, LName text, username text PRIMARY KEY, password text);
CREATE TABLE project_list(ID serial PRIMARY KEY, project_name text, frozen boolean);
CREATE TABLE works_on(project_ID integer, user_id text, FOREIGN KEY (project_ID) references project_list(ID), FOREIGN KEY (user_ID) references user_list(username), role text);
