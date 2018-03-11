module Main exposing (..)

import Array exposing (Array)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as JD
import Json.Decode.Pipeline as PL
import Debug exposing (log)


main =
    Html.program
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL ----------------------------------------------------------------------


{-| Different states of the App.

Different buttons are shown in these states.

-}
type UsageMode
    = MRun
    | MChange
    | MEdit Int


{-| A Search Task roughly as it is represented in JSON.

`SearchTask` represents a search with certain keywords on a specific
server.

-}
type alias SearchTask =
    { id : String
    , queryString : String
    , recurrence : String
    , server : String
    , product : Maybe String
    , nListings : Int
    , priceMin : Float
    , priceMax : Float
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


type alias Model =
    { tasks : Array SearchTask
    , errorMsg : String
    , mode : UsageMode
    , editTask : SearchTaskRaw
    }


init : ( Model, Cmd Msg )
init =
    ( Model Array.empty "" MRun (SearchTaskRaw "" "" "" "" "" "" "" "" "")
    , getTaskList
    )



-- UPDATE ---------------------------------------------------------------------


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


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ReloadTasks ->
            ( { model | tasks = Array.empty }, getTaskList )

        NewTasks (Ok newTasks) ->
            ( { model
                | tasks = Array.append model.tasks (Array.fromList newTasks)
                , errorMsg = ""
              }
            , Cmd.none
            )

        NewTasks (Err err) ->
            ( { model | errorMsg = (toString err) }, Cmd.none )

        ChangeMode (MEdit taskIndex) ->
            ( { model
                | mode = MEdit taskIndex
                , editTask =
                    toSearchTaskRaw
                        (Maybe.withDefault
                            (SearchTask "" "" "" "" Nothing 0 0 0 "")
                            (Array.get taskIndex model.tasks)
                        )
              }
            , Cmd.none
            )

        ChangeMode newMode ->
            ( { model | mode = newMode }, Cmd.none )

        ChangeField field newContents ->
            ( { model
                | editTask = updateField field newContents model.editTask
              }
            , Cmd.none
            )


toSearchTaskRaw : SearchTask -> SearchTaskRaw
toSearchTaskRaw inTask =
    { id = inTask.id
    , queryString = inTask.queryString
    , recurrence = inTask.recurrence
    , server = inTask.server
    , product = "" -- inTask.product
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



-- VIEW ----------------------------------------------------------------------


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
                (let
                    indexedTasks =
                        Array.toIndexedList model.tasks

                    callViewFunc : ( Int, SearchTask ) -> Html Msg
                    callViewFunc ( i, task ) =
                        viewSearchTask model model.mode i task
                 in
                    (List.map callViewFunc indexedTasks)
                )
            ]
        , viewError model
        ]


viewSearchTask : Model -> UsageMode -> Int -> SearchTask -> Html Msg
viewSearchTask model mode index task =
    case mode of
        MEdit id ->
            if id == index then
                viewSearchTaskEdit mode index model.editTask
            else
                viewSearchTaskSimple mode index task

        _ ->
            viewSearchTaskSimple mode index task


viewSearchTaskSimple : UsageMode -> Int -> SearchTask -> Html Msg
viewSearchTaskSimple mode index task =
    tr []
        [ td [] [ viewRowControls mode index ]
        , td [] [ text "-" ] --"product": null,
        , td [] [ text task.queryString ]
        , td [] [ text task.server ]
        , td [] [ text task.recurrence ]
        , td [] [ text (toString task.nListings) ]
        , td [] [ text (toString task.priceMin) ]
        , td [] [ text (toString task.priceMax) ]
        , td [] [ text task.currency ]
        ]


viewSearchTaskEdit : UsageMode -> Int -> SearchTaskRaw -> Html Msg
viewSearchTaskEdit mode index task =
    tr []
        [ td [] [ viewRowControls mode index ]
        , td [] [ text "-" ] --"product": null,
        , td [] [ input [ onInput (ChangeField FQueryString), value task.queryString ] [] ]
        , td [] [ input [ onInput (ChangeField FServer), value task.server ] [] ]
        , td [] [ input [ onInput (ChangeField FRecurrence), value task.recurrence ] [] ]
        , td [] [ input [ onInput (ChangeField FNListings), value task.nListings ] [] ]
        , td [] [ input [ onInput (ChangeField FPriceMin), value task.priceMin ] [] ]
        , td [] [ input [ onInput (ChangeField FPriceMax), value task.priceMax ] [] ]
        , td [] [ input [ onInput (ChangeField FCurrency), value task.currency ] [] ]
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
                    [ button [{- onClick ReloadTasks -}] [ text "Save" ]
                    , button [ onClick (ChangeMode MChange) ] [ text "Revert" ]
                    ]
            else
                div [] []


viewError : Model -> Html Msg
viewError model =
    if model.errorMsg == "" then
        div [] []
    else
        div
            [ style
                [ ( "color", "red" )
                , ( "font-weight", "bold" )
                ]
            ]
            [ text ("Error: " ++ model.errorMsg) ]



-- SUBSCRIPTIONS --------------------------------------------------------------


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- HTTP ----------------------------------------------------------------------


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
