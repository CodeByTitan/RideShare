DELIMITER //
DROP PROCEDURE IF EXISTS getuser //
CREATE PROCEDURE getuser
(
   IN userIdIn int
)
BEGIN
   Select * from users where userId = userIdIn;

    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52714'
        SET MESSAGE_TEXT = 'No matching user found';
    END IF;
END //
DELIMITER ;
