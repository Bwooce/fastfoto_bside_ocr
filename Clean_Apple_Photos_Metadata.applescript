-- Clean Apple Photos Metadata from Pollution
-- Removes contaminated descriptions and keywords from Apple Photos
-- Run this script to clean up photos that have pollution like "leave empty", "no context", etc.

tell application "Photos"
	activate

	-- Get user choice for scope
	set userChoice to display dialog "Clean metadata from:" buttons {"Selected Photos", "All Photos", "Cancel"} default button "Selected Photos" with icon note

	if button returned of userChoice is "Cancel" then
		return
	end if

	-- Initialize counters
	set totalProcessed to 0
	set descriptionsCleared to 0
	set keywordsCleared to 0

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
		set currentPhoto to item i of photoList
		set photoChanged to false

		try
			-- Check and clean description
			set currentDescription to description of currentPhoto
			if currentDescription is not missing value and currentDescription is not "" then
				-- Check for pollution patterns
				if (currentDescription contains "leave empty") or ¬
					(currentDescription contains "no context") or ¬
					(currentDescription contains "back scan") or ¬
					(currentDescription contains "not extractable") or ¬
					(currentDescription contains "no extractable") or ¬
					(currentDescription contains "Leave empty") or ¬
					(currentDescription contains "photo lab") or ¬
					(currentDescription contains "processing") then

					set description of currentPhoto to ""
					set descriptionsCleared to descriptionsCleared + 1
					set photoChanged to true
				end if
			end if

			-- Check and clean keywords
			set currentKeywords to keywords of currentPhoto
			if (count of currentKeywords) > 0 then
				set cleanKeywords to {}
				set keywordsChanged to false

				repeat with keyword in currentKeywords
					set keywordText to keyword as string
					-- Check for pollution patterns in keywords
					if not ((keywordText contains "leave empty") or ¬
						(keywordText contains "no context") or ¬
						(keywordText contains "back scan") or ¬
						(keywordText contains "not extractable") or ¬
						(keywordText contains "none visible") or ¬
						(keywordText contains "Leave empty") or ¬
						(keywordText contains "photo lab") or ¬
						(keywordText contains "processing") or ¬
						(keywordText contains "blank") or ¬
						(keywordText contains "degraded")) then

						set end of cleanKeywords to keywordText
					else
						set keywordsChanged to true
					end if
				end repeat

				-- Update keywords if we removed any pollution
				if keywordsChanged then
					set keywords of currentPhoto to cleanKeywords
					set keywordsCleared to keywordsCleared + 1
					set photoChanged to true
				end if
			end if

			if photoChanged then
				set totalProcessed to totalProcessed + 1
			end if

			-- Show progress every 100 photos
			if (i mod 100) = 0 then
				display notification "Processed " & i & " of " & totalPhotos & " photos..." with title "Cleaning Metadata"
			end if

		on error errMsg
			-- Skip photos that can't be processed
			log "Error processing photo " & i & ": " & errMsg
		end try
	end repeat

	-- Show final results
	set resultMessage to "Metadata cleanup complete!" & return & return
	set resultMessage to resultMessage & "Photos processed: " & totalProcessed & return
	set resultMessage to resultMessage & "Descriptions cleared: " & descriptionsCleared & return
	set resultMessage to resultMessage & "Keywords cleaned: " & keywordsCleared

	display dialog resultMessage buttons {"OK"} with icon note

end tell

-- Alternative version for batch keyword removal
-- Uncomment this section if you want to completely remove all keywords from selected photos

(*
tell application "Photos"
	set photoList to selection
	if (count of photoList) = 0 then
		display dialog "No photos selected." buttons {"OK"}
		return
	end if

	set confirmRemove to display dialog "Remove ALL keywords from " & (count of photoList) & " selected photos?" buttons {"Remove All Keywords", "Cancel"} default button "Cancel"

	if button returned of confirmRemove is "Remove All Keywords" then
		repeat with currentPhoto in photoList
			try
				set keywords of currentPhoto to {}
			end try
		end repeat
		display dialog "All keywords removed from " & (count of photoList) & " photos." buttons {"OK"}
	end if
end tell
*)