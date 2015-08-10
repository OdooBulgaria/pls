-----------------
# SETUP
--------------

## Restrictions

- A user can have only one employee
-  Make sure that the circle manager and project manager have the right hierarchy and an employee. is always there for them also the related user field should be filled
-  To ensure this there is a not null constraint on related user for employees if the user is project manager or circle head 
- Do not delete the default property created by this module for setting the default timings for project manager
- Make sure that there is one employee made for the admin user too otherwise there will lot places where the admin will not be able to override
- Set the attendance cron job timer. During the installation set randomly
- To take project attendance or use attendance functionality it's state should be 'wip'
- Make Sure that Admin gets the corporate account otherwise the cron jobs will not work
- easy_install pytz(for timezone)
- Install the Aeroo Reports. The installation instructions are given in the report folder

## To set up the users and accesses

-  Create all users 
	- Director 
	- Circle Head 
	- Project Manager 
	- Employees
-  Make related user for all the Circle Heads ,Project Manager, Director otherwise they wont be able to see their employee database

> **Do not leave the project managers,circle heads without related users in hr.employee**

-  Access Rights for Telecom Module 
	- Project Manager -
	- Manager
	- Circle Head -- Circle Head , 
	- Admin or Corporate --- Corporate
-  Access Rights for HR Module 

	> **The first three users will be hr employees**

	- Employee 
	- Project Manager 
	- Circle Head should be employee 
	- Corporate and admin will be Manager

------------------------------------
# Attendance Functionality
--------------------------------

> The user who creates the attendance line will show in the created by field
 

## Cron logs
- [x] Unsubmitted attendance lines of each user
	- [x] It could be created by project manager since it is a single man project
	- [x] It culd have been created by other sharing project manager but both of them did not submit it
- [x] Project Manager who did not submit their attendance
- [x] UID who do not have an emp_id
- [x] All attendance.attendance records that are unsubmitted (Warning to close it)

## Attendance Functionality

- [x] Create todays attendance.attendance menuitem `(Done by adding todays filter)` 
- [x] Only when all the project lines are submitted the attendance.attendance will be allowed to be submitted manually
- [x] When any project line is changed to state pending then the attendance record also changes to pending 
 
- [x] when the submit button is clicked the project attendance is submitted

- [x] Create a setting panel where the time limit for attendance can be setup
	- [x] Create a property field to hold  default attendance time in res.users named `permitted_attendance_time`
	- [x] Make ir.property for this field and set the default time to 11:00

- [x] In order to override the time limit the admin will tick on 'Allow overriding the time limit option' in hr.employee to let him override.Every time this option is ticked a note will be logged stating the reason for overriding. Also after one hour that option will close it self. The reason for overriding will be logged to display the project manager monthly report
	- [x] Created a new subtype "overrides"
	- [x] Created Menu item Permission Override Logs 
	
	> Inheritted and customized the default complaint_system module. So that the pls module and complaint_system modules are completely independent of each other

	- [x] Put a restriction on "Take attendance button based on time and permission to override
	- [x] To do this create a field in project manager (res.users,boolean field)
	
- [x] In the submit button there will be a check that if all the project's attendance of that project manager is submitted then attendance will close 

- [x] Check if the attendance is submitted by the corporate or project manager/circle head)
		- [x] If the project manager submits the attendance then the attendance record will get submitted either after allowed time or after all his project attendance is submitted

- [x] If after the allowed time the manager tries to take attendance they wont be allowed until and unless they are allowed to override by admin panel
- [x] The overriding option will always be open for only 1 hour. 

- [x] Create a cron job that does the following
	> **Make sure that 'Allow overriding the time limit option' is taken into consideration each time** 
	- [x] If within the allowed time the attendance.attendance record is not closed then a log for that project manager will be created ('mail.message') and a mail will be dispatched to the follower of that document ("send a message" functionality).
	- [x] Check if the project manager has taken all the attendances. If not then log an internal note 
    - [x] At allowed time the cron job will run and that time automatically all unsubmitted attendances will be submitted and all the project manager attendance.attendance records will close.
	- [x] Once all the attendances are submitted a new cron job will trigger that will check if the manager has taken all the attendances. If not then an internal note will be logged for him and a mail will be dispatched to the follower of the documents
	- [x] A final cron summary will be logged in a seperate document that the admin can check and know the status of everything
		- [x] This will also show the projects for which the attendance was not taken at all

- [ ] Remove the cron button from the attendance and test it with actual cron
- [ ] Create the attendance widget for the project manager
- [ ] Attendance Dash Board 
	- [ ] Corporate
	- [ ] Manager
	- [ ] Circle Head  