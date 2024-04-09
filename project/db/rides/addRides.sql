DELIMITER //
DROP PROCEDURE IF EXISTS addRide //
CREATE PROCEDURE addride
(
    IN startAddressIN     varchar(100),
    IN endAddressIN      varchar(100),
    IN costIN  float(32),
    IN riderIdIN  INT
)
BEGIN
   INSERT INTO rides (startAddress, endAddress, cost, riderId) VALUES (startAddressIN, endAddressIN, costIN, riderIdIN);

    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to create the ride.';
    END IF;

    /* If the INSERT is successful, then this will return the Id for the record */
    SELECT LAST_INSERT_ID(); /* Specific to this session */

END //
DELIMITER ;
