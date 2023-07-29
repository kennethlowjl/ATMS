Features:

- register, login, logout, change password with encrypted passwords.
- user can choose dates to submit attendance.
- dates can be one day, or multiple days.
- user can choose between AM/PM/Full day for the selected day/s.
- once attendance is submitted, it is automatically saved into the calendar style row and column table.
- user can enter month or year of choice and click load calendar to see in full their status.
- user will only be able to view their choice of month in a year per load calendar request.
- all employees attendance records details the attendance submission information -> Date, time, location, status, user.


- for attendance submission regarding OFF, admin1 has the permission to approve or deny the off request.
- only after approving, the OFF status will be updated in the db and calendar view in attendance submission page.
- admin1 can also update any user's off balance by manually typing in the number of days. 
- off balance section displays any incoming requests for off.
- all users off balance displays all users off balance.

- admin1 can assign tasks to any users.
- admin1 or the task assignee have the permission to complete task.
- 2 categories for tasks, To be completed and Completed

- users are able to upload their own profile picture

- current database structure consists of 4 tables with primary/foreign key relations. attendance, tasks, user, off_request

to be implemented/fixed (short term):

- off balance to sync with attendance submission. after off is approved, off balance should be adjusted as well.
- tasks should come with information such as creator, date of creation, due date, subtasks, comment box.
- all users attendance log does not come with the table view with month/year search yet.
- migrate db to SQL.

