-----------------
# SETUP
--------------

## Restrictions

- A user can have only one employee
-  Make sure that the circle manager and project manager have the right hierarchy and an employee. is always there for them also the related user field should be filled
-  To ensure this there is a not null constraint on related user for employees if the user is project manager or circle head 

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

## Manager Note Logging
- [ ] Create a functional field many2many that will automatically fetch all the mail.message regarding that manager and display
	- [ ] For this just enter the related model as "hr.employee"
	- [ ] Create own subtype 
	- [ ] Enter the related id as the id of the project manager 
	- [ ] In the many2many field look for the same subtype
	
	> In short all the mail.message with subtype 'complaints' related document hr.employee and related id = id of employee will give
	> the biodata of the employee (This will be our standard employee log)  
	
## Attendance Functionality

- [x] Only when all the project lines are submitted the attendance.attendance will be allowed to be submitted manually
- [x] When any project line is changed to state pending then the attendance record also changes to pending 
 
- [x] when the submit button is clicked the project attendance is submitted

- [ ] In the submit button there will be a check that if all the project's attendance of that project manager is submitted then attendance will close 

- [ ] Create a setting panel where the time limit for attendance can be setup.

- [ ] In order to override the time limit the admin will tick on 'Allow overriding the time limit option' in hr.employee to let him override.Every time this option is ticked a note will be logged stating the reason for overriding. Also after one hour that option will close it self. The reason for overriding will be logged to display the project manager monthly report
	- [ ] To do this create a field in project manager (hr.employee,boolean field)

- [ ] If after the allowed time the manager tries to take attendance they wont be alowed until and unless they are allowed to override by admin panel
- [ ] The overriding option will always be open for only 1 hour. 

- [ ] Create a cron job that does the following
	> **Make sure that 'Allow overriding the time limit option' is taken into consideration each time** 
	- [ ] If within the allowed time the attendance.attendance record is not closed then a log for that project manager will be created ('mail.message') and a mail will be dispatched to the follower of that document ("send a message" functionality).
	- [ ] Check if the project manager has taken all the attendances. If not then log an internal note 
    - [ ] At allowed time the cron job will run and that time automatically all unsubmitted attendances will be submitted and all the project manager attendance.attendance records will close.
	- [ ] Once all the attendances are submitted a new cron job will trigger that will check if the manager has taken all the attendances. If not then an internal note will be logged for him and a mail will be dispatched to the follower of the documents
	- [ ] A final cron summary will be logged in a seperate document that the admin can check and know the status of everything
		- [ ] This will also show the projects for which the attendace was not taken at all

- [ ] Attendance Dash Board 
	- [ ] Corporate
	- [ ] Manager
	- [ ] Circle Head  