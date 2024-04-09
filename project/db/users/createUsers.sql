DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userId INT         NOT NULL AUTO_INCREMENT,
  userName     varchar(100) NOT NULL,
  email     varchar(100) NOT NULL,
  phoneNumber     varchar(100) NOT NULL,
  PRIMARY KEY (userId)
);
