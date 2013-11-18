CREATE TABLE user_list(FName text, LName text, username text PRIMARY KEY, password text);
CREATE TABLE project_list(ID serial PRIMARY KEY, project_name text);
CREATE TABLE presentation(ID serial PRIMARY KEY, project_ID integer, FOREIGN KEY (project_ID) REFERENCES project_list(ID), version integer, primary_status boolean);
CREATE TABLE slide_list(ID integer PRIMARY KEY, project_ID integer, FOREIGN KEY (project_ID) REFERENCES project_list(ID), version integer, creation_date date, original_ID integer, previous_ID integer, approval_required boolean, approval_status boolean, confidentiality boolean, mandatory_status text, checkout_ID text);
CREATE TABLE presentation_contains(presentation_ID integer, slide_ID integer, FOREIGN KEY(presentation_ID) references presentation(ID), FOREIGN KEY(slide_ID) references slide_list(ID), page_number integer);
CREATE TABLE works_on(project_ID integer, user_id text, FOREIGN KEY (project_ID) references project_list(ID), FOREIGN KEY (user_ID) references user_list(username), role text);
CREATE TABLE opt_out_list(slide_ID integer, user_ID text, opt_out_status boolean, FOREIGN KEY (slide_ID) REFERENCES slide_list(ID), FOREIGN KEY (user_ID) REFERENCES user_list(username));
