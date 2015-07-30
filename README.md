# pls

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


Attendance Workflow --->
 
1. Only when all the project lines are submitted the atendance will be allowed to be submitted manually
2. When any project line is changed to state pending then the attendace record also changes to pending
 
 