# pls
-------
Restrictions ->
1. A user can have only one employee
2. Make sure that the circle manager and project manager have the right hierarchy and an employee. is always there for them also the related user field should be filled
3. To ensure this there is a not null constraint on related user for employees if the user is project manager or circle head 

To set up the users and accesses

1. Create all Director --> Circle Head --> Project Manager ---> Employees
2. Make related user for all the Circle Heads ,Project Manager, Director otherwise they wont be able to see their employee database
3. Warning -: Do not leave the porject managers,circle heads without related users in hr.employee
4. Access Rights for Telecom Module -->Project Manager --> manager , Circle Head --> Circle Head , Admin or Corporrate ---> Corporate
5. Access Rights for HR Module --> Employee, Project Manager,Circle Head should be employee and the corporate and admin will be manager


#Attendance Workflow --->
------------------- 
- [x] Only when all the project lines are submitted the attendance.attendance will be allowed to be submitted manually
- [] When any project line is changed to state pending then the attendance record also changes to pending 
 
Attendance Functionality

* when the submit button is clicked the project attendance is submitted

* In the submit button there will be a check that if all the project's attendance of that project manager is submitted then attendance will close 

* If within the allowed time the attendance.attendance record is not closed then a log for that project manager will be created ('mail.message') and a mail will be dispatched to the follower of that document ("send a message" functionality)

* At allowed time the cron job will run and that time automatically all unsubmitted attendances will be submitte and all the project manager attendance.attendance records will close.

* In order to override the time limit the admin will tick on "Allow overriding the time limit option" in hr.employee to let him override.Every time this option is ticked a note will be logged stating the reason for overriding. Also after one hour that option will close it self. The reason for overriding will be logged to display the project manager monthly report

* Once all the attendances are submitted a new cron job will trigger that will check if the manager has taken all the attendances. If not then an internal note will be logged for him and a mail will be dispatched to the follower of the documents
 