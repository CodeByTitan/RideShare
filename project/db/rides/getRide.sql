DELIMITER //
DROP PROCEDURE IF EXISTS getride //
CREATE PROCEDURE getride
(
   IN rideIdIn int
)
BEGIN
   Select * from rides where rideId = rideIdIn;

    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52714'
        SET MESSAGE_TEXT = 'No matching ride found';
    END IF;
END //
DELIMITER ;
