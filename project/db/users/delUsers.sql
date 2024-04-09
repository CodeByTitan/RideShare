DELIMITER //
DROP PROCEDURE IF EXISTS deluser //
CREATE PROCEDURE deluser
(
   IN deleteID INT
)
BEGIN
   DELETE FROM users where userId = deleteID;

   IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52712'
        SET MESSAGE_TEXT = 'Unable to delete the user.';
    END IF;
END //
DELIMITER ;
