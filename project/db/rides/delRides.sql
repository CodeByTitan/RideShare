DELIMITER //
DROP PROCEDURE IF EXISTS delride //
CREATE PROCEDURE delride
(
   IN deleteID INT
)
BEGIN
   DELETE FROM rides where rideId = deleteID;
   IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52712'
        SET MESSAGE_TEXT = 'Unable to delete the user.';
    END IF;
END //
DELIMITER ;
