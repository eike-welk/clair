module Main exposing (..)

import Array exposing (Array)
import Maybe exposing (withDefault)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as JD
import Json.Decode.Pipeline as PL


--import Debug exposing (log)


main =
    Html.program
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL ----------------------------------------------------------------------
-------------------------------------------------------------------------------


{-| Different states of the App.

Different buttons are shown in these states.

-}
type UsageMode
    = MRun
    | MChange
    | MEdit Int


{-| A Search Task roughly as it is represented in JSON.

A `SearchTask` represents a search with certain keywords on a specific server.
A search task is a record in the data base.

-}
type alias SearchTask =
    { -- The data base ID
      id : String

    -- The words used in the search query.
    , queryString : String

    -- Time between two searches. Format: "days hh:mm:ss"
    , recurrence : String

    -- String representing the Server where the search is executed.
    , server : String

    -- API URL of the product
    , product : Maybe String

    -- The desired number of listings that should be returned.
    , nListings : Int

    -- The minimum price of each listing.
    , priceMin : Float

    -- The maximum price of each listing.
    , priceMax : Float

    -- The currency for the maximum- and minimum prices.
    , currency : String
    }


{-| The contents of all input fields for editing the `SearchTask`.
-}
type alias SearchTaskRaw =
    { id : String
    , queryString : String
    , recurrence : String
    , server : String
    , product : String
    , nListings : String
    , priceMin : String
    , priceMax : String
    , currency : String
    }


{-| Errors for all input fields for editing the `SearchTask`.
-}
type alias SearchTaskError =
    { --id : String
      queryString : Maybe String
    , recurrence : Maybe String
    , server : Maybe String
    , product : Maybe String
    , nListings : Maybe String
    , priceMin : Maybe String
    , priceMax : Maybe String
    , currency : Maybe String
    }


type alias Model =
    { tasks : Array SearchTask
    , generalError : String
    , mode : UsageMode
    , editTask : SearchTaskRaw
    , editError : SearchTaskError
    }


init : ( Model, Cmd Msg )
init =
    ( Model Array.empty
        ""
        MRun
        (SearchTaskRaw "" "" "" "" "" "" "" "" "")
        (SearchTaskError Nothing Nothing Nothing Nothing Nothing Nothing Nothing Nothing)
    , getTaskList
    )



-- UPDATE ---------------------------------------------------------------------
-------------------------------------------------------------------------------


type FormField
    = FRecurrence
    | FServer
    | FProduct
    | FQueryString
    | FNListings
    | FPriceMin
    | FPriceMax
    | FCurrency


type Msg
    = ReloadTasks
    | NewTasks (Result Http.Error (List SearchTask))
    | ChangeMode UsageMode
    | ChangeField FormField String
    | SaveEdit
    | SaveResponse (Result Http.Error String)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ReloadTasks ->
            ( { model | tasks = Array.empty }, getTaskList )

        NewTasks (Ok newTasks) ->
            ( { model
                | tasks = Array.append model.tasks (Array.fromList newTasks)
                , generalError = ""
              }
            , Cmd.none
            )

        NewTasks (Err err) ->
            ( { model | generalError = (toString err) }, Cmd.none )

        ChangeMode (MEdit iTask) ->
            let
                newEditTask =
                    toSearchTaskRaw
                        (Array.get iTask model.tasks
                            |> withDefault (SearchTask "" "" "" "" Nothing 0 0 0 "")
                        )

                newEditError =
                    validateEditTask newEditTask
            in
                ( { model
                    | mode = MEdit iTask
                    , editTask = newEditTask
                    , editError = newEditError
                  }
                , Cmd.none
                )

        ChangeMode newMode ->
            ( { model | mode = newMode }, Cmd.none )

        ChangeField field newContents ->
            let
                newEditTask =
                    updateField field newContents model.editTask

                newEditError =
                    validateEditTask newEditTask
            in
                ( { model
                    | editTask = newEditTask
                    , editError = newEditError
                  }
                , Cmd.none
                )

        SaveEdit ->
            ( model, saveEditTask )

        SaveResponse (Ok msg) ->
            ( { model | mode = MChange }, Cmd.none )

        SaveResponse (Err err) ->
            ( { model | generalError = (toString err) }, Cmd.none )


toSearchTaskRaw : SearchTask -> SearchTaskRaw
toSearchTaskRaw inTask =
    { id = inTask.id
    , queryString = inTask.queryString
    , recurrence = inTask.recurrence
    , server = inTask.server
    , product = inTask.product |> withDefault ""
    , nListings = toString inTask.nListings
    , priceMin = toString inTask.priceMin
    , priceMax = toString inTask.priceMax
    , currency = inTask.currency
    }


updateField : FormField -> String -> SearchTaskRaw -> SearchTaskRaw
updateField field newContents task =
    case field of
        FRecurrence ->
            { task | recurrence = newContents }

        FServer ->
            { task | server = newContents }

        FProduct ->
            { task | product = newContents }

        FQueryString ->
            { task | queryString = newContents }

        FNListings ->
            { task | nListings = newContents }

        FPriceMin ->
            { task | priceMin = newContents }

        FPriceMax ->
            { task | priceMax = newContents }

        FCurrency ->
            { task | currency = newContents }


trimStringsEditTask : SearchTaskRaw -> SearchTaskRaw
trimStringsEditTask task =
    { task
        | id = String.trim task.id
        , queryString = String.trim task.queryString
        , recurrence = String.trim task.recurrence
        , server = String.trim task.server
        , product = String.trim task.product
        , nListings = String.trim task.nListings
        , priceMin = String.trim task.priceMin
        , priceMax = String.trim task.priceMax
        , currency = String.trim task.currency
    }


validateEditTask : SearchTaskRaw -> SearchTaskError
validateEditTask taskIn =
    let
        task =
            trimStringsEditTask taskIn
    in
        { queryString =
            if task.product == "" && task.queryString == "" then
                Just "A query string is required."
            else
                Nothing
        , product =
            if task.product == "" && task.queryString == "" then
                Just "A product or query string is required."
            else
                -- TODO: Test if product exists
                Nothing
        , recurrence =
            if task.recurrence == "" then
                Just "The recurrence must be specified."
            else
                Nothing
        , server =
            if task.server == "" then
                Just "The server must be specified."
            else
                Nothing
        , nListings =
            let
                rawNum =
                    task.nListings

                convNum =
                    String.toInt rawNum
            in
                case ( rawNum, convNum ) of
                    ( "", _ ) ->
                        Just "The number of listings must be specified."

                    ( "+", _ ) ->
                        Just "A positive whole number is required."

                    ( "-", _ ) ->
                        Just "A positive whole number is required."

                    ( _, Err _ ) ->
                        Just "A positive whole number is required."

                    ( _, Ok num ) ->
                        if num < 0 then
                            Just "The number must be positive."
                        else
                            Nothing
        , priceMin =
            let
                rawNum =
                    task.priceMin

                convNum =
                    String.toFloat rawNum
            in
                case ( rawNum, convNum ) of
                    ( "", _ ) ->
                        Just "The minimum price must be specified."

                    ( _, Err _ ) ->
                        Just "A positive number is required."

                    ( _, Ok num ) ->
                        if num < 0 then
                            Just "The number must be positive."
                        else
                            Nothing
        , priceMax =
            let
                rawNum =
                    task.priceMax

                convNum =
                    String.toFloat rawNum

                convMin =
                    String.toFloat task.priceMin |> Result.withDefault 0
            in
                case ( rawNum, convNum ) of
                    ( "", _ ) ->
                        Just "The maximum price must be specified."

                    ( _, Err _ ) ->
                        Just "A positive number is required."

                    ( _, Ok num ) ->
                        if num < 0 then
                            Just "The number must be positive."
                        else if num < convMin then
                            Just "The minimum value must be <= the maximum value."
                        else
                            Nothing
        , currency =
            if task.currency == "" then
                Just "The currency must be specified."
            else
                Nothing
        }



-- VIEW ----------------------------------------------------------------------
-------------------------------------------------------------------------------


view : Model -> Html Msg
view model =
    div []
        [ h2 [] [ text "Search Tasks" ]
        , br [] []
        , div []
            [ button [ onClick (ChangeMode MRun) ] [ text "Run" ]
            , button [ onClick (ChangeMode MChange) ] [ text "Change" ]
            , button [ onClick ReloadTasks ] [ text "Reload" ]
            ]
        , table []
            [ thead []
                [ tr []
                    [ th [] [ text "Controls" ]
                    , th [] [ text "Product" ]
                    , th [] [ text "Query String" ]
                    , th [] [ text "Server" ]
                    , th [] [ text "Recurrence" ]
                    , th [] [ text "Number Listings" ]
                    , th [] [ text "Price Min" ]
                    , th [] [ text "Price Max" ]
                    , th [] [ text "Currency" ]
                    ]
                ]
            , tbody []
                (List.map
                    (\( i, task ) -> viewSearchTask model model.mode i task)
                    (Array.toIndexedList model.tasks)
                )
            ]
        , viewError model
        ]


viewSearchTask : Model -> UsageMode -> Int -> SearchTask -> Html Msg
viewSearchTask model mode index task =
    case mode of
        MEdit id ->
            if id == index then
                viewSearchTaskEdit index model.editTask model.editError
            else
                viewSearchTaskSimple mode index task

        _ ->
            viewSearchTaskSimple mode index task


viewSearchTaskSimple : UsageMode -> Int -> SearchTask -> Html Msg
viewSearchTaskSimple mode index task =
    tr []
        [ td [] [ viewRowControls mode index ]
        , td [] [ text "-" ] -- API URL of the product
        , td [] [ text task.queryString ]
        , td [] [ text task.server ]
        , td [] [ text task.recurrence ]
        , td [] [ text (toString task.nListings) ]
        , td [] [ text (toString task.priceMin) ]
        , td [] [ text (toString task.priceMax) ]
        , td [] [ text task.currency ]
        ]


viewSearchTaskEdit : Int -> SearchTaskRaw -> SearchTaskError -> Html Msg
viewSearchTaskEdit index task error =
    tr []
        [ td [] [ viewRowControls (MEdit index) index ]
        , td [] [ text "-" ] -- API URL of the product
        , td [] [ viewInputWithError (ChangeField FQueryString) task.queryString error.queryString ]
        , td [] [ viewInputWithError (ChangeField FServer) task.server error.server ]
        , td [] [ viewInputWithError (ChangeField FRecurrence) task.recurrence error.recurrence ]
        , td [] [ viewInputWithError (ChangeField FNListings) task.nListings error.nListings ]
        , td [] [ viewInputWithError (ChangeField FPriceMin) task.priceMin error.priceMin ]
        , td [] [ viewInputWithError (ChangeField FPriceMax) task.priceMax error.priceMax ]
        , td [] [ viewInputWithError (ChangeField FCurrency) task.currency error.currency ]
        ]


viewInputWithError : (String -> Msg) -> String -> Maybe String -> Html Msg
viewInputWithError callBack currentValue error =
    case error of
        Nothing ->
            div []
                [ input [ onInput callBack, value currentValue ] [] ]

        Just errorMessage ->
            div []
                [ input
                    [ style [ ( "background-color", "#ffe6ea" ) ]
                    , onInput callBack
                    , value currentValue
                    ]
                    []
                , br [] []
                , label [ style [ ( "color", "red" ) ] ] [ text errorMessage ]
                ]


viewRowControls : UsageMode -> Int -> Html Msg
viewRowControls mode currentID =
    case mode of
        MRun ->
            div []
                [ button [{- onClick ReloadTasks -}] [ text "Run" ]
                ]

        MChange ->
            div []
                [ button [{- onClick ReloadTasks -}] [ text "Delete" ]
                , button [ onClick (ChangeMode (MEdit currentID)) ] [ text "Edit" ]
                ]

        MEdit id ->
            if id == currentID then
                div []
                    [ button [ onClick SaveEdit ] [ text "Save" ]
                    , button [ onClick (ChangeMode MChange) ] [ text "Revert" ]
                    ]
            else
                div [] []


viewError : Model -> Html Msg
viewError model =
    if model.generalError == "" then
        div [] []
    else
        div
            [ style
                [ ( "color", "red" )
                , ( "font-weight", "bold" )
                ]
            ]
            [ text ("Error: " ++ model.generalError) ]



-- SUBSCRIPTIONS --------------------------------------------------------------
-------------------------------------------------------------------------------


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- HTTP ----------------------------------------------------------------------
-------------------------------------------------------------------------------


{-| The API URL for accessing search tasks.
-}
url_SEARCH_TASKS : String
url_SEARCH_TASKS =
    --"/collect/api/search_tasks/"
    "http://localhost:8000/collect/api/search_tasks/"


getTaskList : Cmd Msg
getTaskList =
    Http.send NewTasks (Http.get url_SEARCH_TASKS parseSearchTaskList)


{-| Parse the JSON response from the "Search Tasks" API.

The JSON has the following form:

    """
    {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "recurrence": "3 00:00:00",
                "server": "EBAY-DE",
                "product": null,
                "query_string": "Nikon D90",
                "n_listings": 50,
                "price_min": 100.0,
                "price_max": 500.0,
                "currency": "EUR"
            },
            {...}
        ]
    }
    """

-}
parseSearchTaskList : JD.Decoder (List SearchTask)
parseSearchTaskList =
    JD.at [ "results" ]
        (JD.list
            (PL.decode SearchTask
                |> PL.required "id" (JD.map toString JD.int)
                |> PL.required "query_string" JD.string
                |> PL.required "recurrence" JD.string
                |> PL.required "server" JD.string
                |> PL.required "product" (JD.nullable JD.string)
                |> PL.required "n_listings" JD.int
                |> PL.required "price_min" JD.float
                |> PL.required "price_max" JD.float
                |> PL.required "currency" JD.string
            )
        )


saveEditTask : Cmd Msg
saveEditTask =
    Http.send SaveResponse (Http.post url_SEARCH_TASKS Http.emptyBody parsePostResponse)


parsePostResponse : JD.Decoder String
parsePostResponse =
    JD.string
