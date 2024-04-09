DELIMITER //
DROP PROCEDURE IF EXISTS addDriver //
CREATE PROCEDURE addDriver
(
    IN driverIdIN INT,
    IN rideIdIN INT
)
BEGIN
   UPDATE rides
   SET rideStatus = 'Driver Found', driverId = driverIdIN
   WHERE rideId = rideIdIN;
   
    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52714'
        SET MESSAGE_TEXT = 'Unable to find the ride.';
    END IF;

END //
DELIMITER ;
