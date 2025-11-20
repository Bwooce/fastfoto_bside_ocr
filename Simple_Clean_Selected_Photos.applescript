-- Simple Apple Photos Metadata Cleaner
-- Removes pollution descriptions and keywords from selected photos only

tell application "Photos"
	activate

	set photoList to selection
	if (count of photoList) = 0 then
		display dialog "Please select photos in Apple Photos first, then run this script." buttons {"OK"} with icon caution
		return
	end if

	set confirmClean to display dialog "Remove pollution metadata from " & (count of photoList) & " selected photos?" buttons {"Clean Metadata", "Cancel"} default button "Clean Metadata"

	if button returned of confirmClean is "Cancel" then
		return
	end if

	set cleaned to 0

	repeat with currentPhoto in photoList
		try
			-- Clear description if it contains pollution
			set desc to description of currentPhoto
			if desc is not missing value and desc is not "" then
				if (desc contains "leave empty") or (desc contains "no context") or (desc contains "back scan") or (desc contains "not extractable") then
					set description of currentPhoto to ""
					set cleaned to cleaned + 1
				end if
			end if

			-- Remove pollution keywords
			set currentKeywords to keywords of currentPhoto
			if (count of currentKeywords) > 0 then
				set cleanKeywords to {}
				repeat with keyword in currentKeywords
					set keywordText to keyword as string
					if not ((keywordText contains "leave empty") or (keywordText contains "no context") or (keywordText contains "none visible") or (keywordText contains "blank")) then
						set end of cleanKeywords to keywordText
					end if
				end repeat
				set keywords of currentPhoto to cleanKeywords
			end if

		end try
	end repeat

	display dialog "Cleaned " & cleaned & " photos successfully!" buttons {"OK"} with icon note

end tell