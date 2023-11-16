import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):

    notification_id = msg.get_body().decode('utf-8')
    logging.info(
        'Python ServiceBus queue trigger processed message: %s', notification_id)

    # Update connection string information
    host = "migratingcloudserver.postgres.database.azure.com"
    dbname = "techconfdb"
    user = "migratingcloudserver@migratingcloudserver"
    password = "Admin123@.;"
    sslmode = "require"

    # Send email information
    fromEmail = ""
    sendGridAPIKey = ""

    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
        host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)
    print("Connection established")
    cursor = conn.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        # Fetch all rows from table
        getNotificationQuery = "SELECT * FROM notification WHERE ID = " + notification_id + ";"
        cursor.execute(getNotificationQuery)
        notificationRow = cursor.fetchall()

        # TODO: Get attendees email and name
        getAttendeesQuery = "SELECT * FROM attendee;"
        cursor.execute(getAttendeesQuery)
        attendeeRows = cursor.fetchall()

        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendeeRows:
            message = Mail(
                from_email=fromEmail,
                to_emails=attendee.email,
                subject = '{}: {}'.format(attendee.first_name, notificationRow.subject),
                plain_text_content=notificationRow.message)

            sg = SendGridAPIClient(sendGridAPIKey)
            sg.send(message)

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        notificationRow.completed_date = datetime.utcnow()
        notificationRow.status = 'Notified {} attendees'.format(len(attendeeRows))

        # Cleanup
        conn.commit()
        cursor.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        logging.info('Start finally')
        # TODO: Close connection
