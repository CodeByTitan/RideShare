DELIMITER //
DROP PROCEDURE IF EXISTS getAvailableRides //
CREATE PROCEDURE getAvailableRides()
BEGIN
   Select * from rides where rideStatus = 'Awaiting driver';
END //
DELIMITER ;
