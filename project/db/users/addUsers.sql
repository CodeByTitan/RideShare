DELIMITER //
DROP PROCEDURE IF EXISTS adduser //
CREATE PROCEDURE adduser
(
   IN userNameIn varchar(50),
   IN emailIn varchar(50),
   IN phoneNumber varchar(50)
)
BEGIN
   INSERT INTO users (userName, email, phoneNumber) VALUES (userNameIn, emailIn, phoneNumber);

    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to create the user.';
    END IF;

    /* If the INSERT is successful, then this will return the Id for the record */
    SELECT LAST_INSERT_ID(); /* Specific to this session */

END //
DELIMITER ;
