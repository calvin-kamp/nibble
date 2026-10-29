from config.exceptions import Conflict


class WeightEntryExists(Conflict):
    default_code = "weight_entry_exists"
    default_detail = "Für diesen Tag gibt es schon einen Gewichtseintrag."
