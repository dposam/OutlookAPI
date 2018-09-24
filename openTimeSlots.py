#finds open time slots between events
def findOpenTimeSlots(Events):

	#range of time the events are located at
	#store this value in seperate file config.py
	startDay = '06:00'
	endDay = '18:00'

	num_of_events = 0

	dictStartTime = {}
	dictEndTime = {}
	dictOpenSlots = {}

	index = 0

	if not Events:
		print('no events found for this particular time')
		tuple1 = (startDay, endDay)
		dictOpenSlots[0] = tuple1
		return dictOpenSlots

	else:
		for event in Events:
			num_of_events = num_of_events + 1
			#get start and end time of each event and store in dictionary
			dictStartTime[num_of_events] = event['start']['dateTime'][11:16]
			dictEndTime[num_of_events] = event['end']['dateTime'][11:16]

		#if first event comes after starting time range
		#capture the time slot between starting time range and first event start time
		if(startDay != dictStartTime[1]):
			tuple1 = (startDay, dictStartTime[1])
			dictOpenSlots[0] = tuple1
			index = index + 1;

		for i in range(1,num_of_events+1):
			if i<num_of_events:
				tuple1 = (dictEndTime[i], dictStartTime[i+1])
				dictOpenSlots[i] = tuple1
				index = index + 1;

		#if last event ends before the day is over then 
		# find the time slot between last event and end time
		if (endDay != dictEndTime[num_of_events]):
			tuple1 = (dictEndTime[num_of_events], endDay)
			dictOpenSlots[index] = tuple1


		return dictOpenSlots
		

		