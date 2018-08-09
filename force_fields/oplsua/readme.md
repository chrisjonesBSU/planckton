# OPLS-UA Parsing

## Conversion methods
* To convert angstroms to nano meters, a conversion factor of 1/10 is used.
* To convert kcal/mol to kJ/mol, a conversion factor of 4.184 is used.
* To convert kcal/(Å**2 mol) to kJ/(nm**2 mol), a conversion factor of 4.184 * 100 is used.

## Notes
* Line 155 in opls.sb has a duplicate param, but different K and r, not sure how to handel this, 
in opls.sb.edits, I've renamed the HO to HM to reflect the authors last name, but nothing will ever
be typed HM. 
