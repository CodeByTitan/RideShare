DELIMITER //
DROP PROCEDURE IF EXISTS updateuser //
CREATE PROCEDURE updateuser
(
  IN userIdIn int,
  IN userNameIn varchar(50),
  IN emailIn varchar(50),
  IN phoneNumberIn varchar(50)
)
BEGIN
  UPDATE users
  SET userName = userNameIn, email = emailIn, phoneNumber = phoneNumberIn
  WHERE userId = userIdIn;
 
   IF(ROW_COUNT() = 0) THEN
     SIGNAL SQLSTATE '52714'
       SET MESSAGE_TEXT = 'Unable to find the user.';
   END IF;
END //
DELIMITER ;
