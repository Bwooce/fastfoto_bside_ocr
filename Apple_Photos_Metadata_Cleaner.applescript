-- Comprehensive Apple Photos Metadata Cleaner
-- Removes pollution descriptions and keywords from Apple Photos
-- Also fixes semicolon-separated keywords by splitting them into individual keywords
-- Works with selected photos or entire library

tell application "Photos"
	activate

	-- Get user choice for scope
	set userChoice to display dialog "Clean and fix metadata from:" buttons {"Selected Photos", "All Photos", "Cancel"} default button "Selected Photos" with icon note

	if button returned of userChoice is "Cancel" then
		return
	end if

	-- Initialize counters
	set totalProcessed to 0
	set descriptionsCleared to 0
	set keywordsFixed to 0

	-- Get photos to process
	if button returned of userChoice is "Selected Photos" then
		set photoList to selection
		if (count of photoList) = 0 then
			display dialog "No photos selected. Please select photos first." buttons {"OK"} with icon caution
			return
		end if
	else
		-- Get all photos (this could be slow for large libraries)
		set confirmAll to display dialog "This will process ALL photos in your library. This may take a long time. Continue?" buttons {"Yes", "Cancel"} default button "Cancel" with icon caution
		if button returned of confirmAll is "Cancel" then
			return
		end if
		set photoList to every media item
	end if

	-- Show progress
	set totalPhotos to count of photoList
	display dialog "Processing " & totalPhotos & " photos..." buttons {"Start"} giving up after 3

	-- Process each photo
	repeat with i from 1 to count of photoList
		set photoChanged to false
		set currentPhoto to missing value

		-- Get the current item
		set currentPhoto to item i of photoList

		-- Debug: Check what type of item this is
		set itemClass to missing value
		set itemName to ""
		try
			set itemClass to class of currentPhoto
			set itemName to name of currentPhoto
		on error errMsg
			display dialog "Error getting properties for item " & i & ": " & errMsg buttons {"Continue", "Stop"} default button "Continue" giving up after 3
			if button returned of result is "Stop" then exit repeat
		end try

			-- Only process media items (photos/videos), skip albums, folders, etc.
			if itemClass is missing value then
				-- Skip this item
			else if itemClass is not media item then
				display dialog "Skipping item " & i & " (" & itemName & ") - Not a media item (class: " & (itemClass as string) & ")" buttons {"Continue"} giving up after 2
			else
				-- This is a media item, process it

				-- Check and clean description
				set currentDescription to ""
				try
					set tempDescription to description of currentPhoto
					if tempDescription is not missing value then
						set currentDescription to tempDescription as string
					end if
				on error errMsg
					display dialog "Warning: Could not get description for photo " & i & " (" & itemName & "): " & errMsg buttons {"Continue"} giving up after 2
				end try

				if currentDescription is not "" then
					-- Check for pollution patterns
					if (currentDescription contains "leave empty") or ¬
						(currentDescription contains "no context") or ¬
						(currentDescription contains "back scan") or ¬
						(currentDescription contains "not extractable") or ¬
						(currentDescription contains "no extractable") or ¬
						(currentDescription contains "Leave empty") or ¬
						(currentDescription contains "photo lab") or ¬
						(currentDescription contains "processing") or ¬
						(currentDescription contains "empty - no") or ¬
						(currentDescription contains "(blank") or ¬
						(currentDescription contains "(none") or ¬
						(currentDescription contains "no event/location context") or ¬
						(currentDescription contains "no clear context") or ¬
						(currentDescription contains "no text content") or ¬
						(currentDescription contains "no text present") or ¬
						(currentDescription contains "no text to transcribe") or ¬
						(currentDescription contains "Unable to determine context") or ¬
						(currentDescription contains "Severely faded") or ¬
						(currentDescription contains "Photo lab processing code") or ¬
						(currentDescription contains "Photo lab processing markings") or ¬
						(currentDescription contains "Photo lab processing data") or ¬
						(currentDescription contains "APS processing data") or ¬
						(currentDescription contains "Kodak APS processing") or ¬
						(currentDescription contains "Film processing") or ¬
						(currentDescription contains "technical processing codes") or ¬
						(currentDescription contains "no legible metadata") or ¬
						(currentDescription contains "(none - blank photo back)") or ¬
						(currentDescription contains "text too small") or ¬
						(currentDescription contains "unclear to transcribe") or ¬
						(currentDescription contains "uncertain: faded machine-printed") or ¬
						(currentDescription contains "uncertain: wavy line") or ¬
						(currentDescription contains "Multiple European locations") or ¬
						(currentDescription contains "Kodak Advanced Photo System") or ¬
						(currentDescription contains "machine-printed text not clearly") then

						try
							set description of currentPhoto to ""
							set descriptionsCleared to descriptionsCleared + 1
							set photoChanged to true
						on error errMsg
							display dialog "Error clearing description for photo " & i & " (" & itemName & "): " & errMsg buttons {"Continue"} giving up after 2
						end try
					end if
				end if

				-- Fix keywords: remove pollution and split semicolon-separated keywords
				set currentKeywords to {}
				try
					set tempKeywords to keywords of currentPhoto
					if tempKeywords is not missing value then
						set currentKeywords to tempKeywords
					end if
				on error errMsg
					display dialog "Warning: Could not get keywords for photo " & i & " (" & itemName & "): " & errMsg buttons {"Continue"} giving up after 2
				end try

				if (count of currentKeywords) > 0 then
					set fixedKeywords to {}
					set keywordsChanged to false

					repeat with keyword in currentKeywords
						set keywordText to keyword as string

						-- Skip pollution keywords
						if not ((keywordText contains "leave empty") or ¬
							(keywordText contains "no context") or ¬
							(keywordText contains "back scan") or ¬
							(keywordText contains "not extractable") or ¬
							(keywordText contains "none visible") or ¬
							(keywordText contains "Leave empty") or ¬
							(keywordText contains "photo lab") or ¬
							(keywordText contains "processing") or ¬
							(keywordText contains "blank") or ¬
							(keywordText contains "degraded") or ¬
							(keywordText contains "empty - no") or ¬
							(keywordText contains "(none") or ¬
							(keywordText contains "no extractable") or ¬
							(keywordText contains "no metadata") or ¬
							(keywordText contains "no data extracted") or ¬
							(keywordText contains "lab processing") or ¬
							(keywordText contains "processing codes") or ¬
							(keywordText contains "technical codes") or ¬
							(keywordText contains "insufficient readable") or ¬
							(keywordText contains "lab data") or ¬
							(keywordText contains "processing data") or ¬
							(keywordText contains "metadata elements") or ¬
							(keywordText contains "clear extractable") or ¬
							(keywordText contains "text too small") or ¬
							(keywordText contains "unclear to transcribe") or ¬
							(keywordText contains "uncertain: faded machine-printed") or ¬
							(keywordText contains "uncertain: wavy line") or ¬
							(keywordText contains "Multiple European locations") or ¬
							(keywordText contains "Kodak Advanced Photo System") or ¬
							(keywordText contains "machine-printed text not clearly")) then

							-- Check if keyword contains semicolons
							if keywordText contains ";" then
								-- Split on semicolons and add individual keywords
								set keywordParts to my splitText(keywordText, ";")
								repeat with keywordPart in keywordParts
									set trimmedPart to my trimText(keywordPart as string)
									if trimmedPart is not "" then
										set end of fixedKeywords to trimmedPart
									end if
								end repeat
								set keywordsChanged to true
							else
								-- Keep keyword as-is
								set end of fixedKeywords to keywordText
							end if
						else
							-- Pollution keyword removed
							set keywordsChanged to true
						end if
					end repeat

					-- Update keywords if we made any changes
					if keywordsChanged then
						try
							set keywords of currentPhoto to fixedKeywords
							set keywordsFixed to keywordsFixed + 1
							set photoChanged to true
						on error errMsg
							display dialog "Error updating keywords for photo " & i & " (" & itemName & "): " & errMsg buttons {"Continue"} giving up after 2
						end try
					end if
				end if

				if photoChanged then
					set totalProcessed to totalProcessed + 1
				end if
			end if

			-- Show progress every 50 photos
			if (i mod 50) = 0 then
				display notification "Processed " & i & " of " & totalPhotos & " photos..." with title "Cleaning Metadata"
			end if
	end repeat

	-- Show final results
	set resultMessage to "Metadata cleanup complete!" & return & return
	set resultMessage to resultMessage & "Photos processed: " & totalProcessed & return
	set resultMessage to resultMessage & "Descriptions cleared: " & descriptionsCleared & return
	set resultMessage to resultMessage & "Keywords fixed: " & keywordsFixed

	display dialog resultMessage buttons {"OK"} with icon note

end tell

-- Helper function to split text on delimiter
on splitText(theText, delimiter)
	set AppleScript's text item delimiters to delimiter
	set textItems to text items of theText
	set AppleScript's text item delimiters to ""
	return textItems
end splitText

-- Helper function to trim whitespace
on trimText(theText)
	repeat while theText starts with " " or theText starts with tab
		set theText to text 2 thru -1 of theText
	end repeat
	repeat while theText ends with " " or theText ends with tab
		set theText to text 1 thru -2 of theText
	end repeat
	return theText
end trimText